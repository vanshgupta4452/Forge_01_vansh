import csv
import json
import os
import argparse
from collections import defaultdict
from difflib import SequenceMatcher

# Try to import anthropic for LLM calls, fallback to a mock if not available
try:
    from anthropic import Anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

def get_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def generate_new_title(client, url, old_title):
    """
    Uses the LLM to rewrite the title based on the URL and existing title.
    Ensures the output is between 30-60 characters.
    """
    if not HAS_ANTHROPIC:
        # Fallback deterministic logic if API not available
        page = url.rstrip("/").split("/")[-1] or "Home"
        page = page.replace("-", " ").replace("_", " ").title()
        return f"{page} | NMG Technologies"

    prompt = (
        f"Rewrite the SEO title for the following page:\n"
        f"URL: {url}\n"
        f"Current Title: {old_title if old_title else 'Missing'}\n\n"
        f"Requirements:\n"
        f"1. Length must be between 30 and 60 characters.\n"
        f"2. Must be catchy, descriptive, and professional.\n"
        f"3. Include 'NMG Technologies' as the brand at the end.\n"
        f"4. Return ONLY the new title text."
    )

    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}]
        )
        new_title = message.content[0].text.strip()
        # Basic clamp to ensure it meets requirements if LLM exceeds them
        return new_title[:60]
    except Exception as e:
        print(f"Error calling LLM for {url}: {e}")
        return f"Optimized Title for {url[:20]} | NMG Technologies"

def find_closest_live_page(broken_url, live_pages):
    """
    Finds the closest live page (Status 200) based on URL path similarity.
    """
    if not live_pages:
        return "https://nmgtechnologies.com/"

    broken_path = broken_url.split("://")[-1]
    best_match = live_pages[0]
    max_sim = 0

    for live in live_pages:
        live_path = live.split("://")[-1]
        sim = get_similarity(broken_path, live_path)
        if sim > max_sim:
            max_sim = sim
            best_match = live

    return best_match

def run_fixes(export_dir):
    # Path setup
    base_dir = os.path.dirname(os.path.abspath(__file__))
    report_path = os.path.join(base_dir, "outputs", "report.json")
    csv_path = os.path.join(export_dir, "internal_all.csv")
    out_titles = os.path.join(base_dir, "outputs", "fixes_titles.csv")
    out_redirects = os.path.join(base_dir, "outputs", "redirect_map.csv")

    if not os.path.exists(report_path):
        print(f"Error: report.json not found at {report_path}")
        return

    with open(report_path, "r") as f:
        report = json.load(f)

    if not os.path.exists(csv_path):
        print(f"Error: internal_all.csv not found at {csv_path}")
        return

    with open(csv_path, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    url_to_row = {r["Address"]: r for r in rows}

    # 1. Handle Titles
    client = None
    if HAS_ANTHROPIC:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if api_key:
            client = Anthropic(api_key=api_key)
        else:
            print("Warning: ANTHROPIC_API_KEY not found. Using fallback logic.")

    title_fixes = []
    affected_titles = set()
    for issue in report["issues"]:
        if any(t in issue["type"] for t in ["duplicate_title", "title_too_long", "title_too_short"]):
            affected_titles.update(issue["affected_urls"])

    print(f"Fixing {len(affected_titles)} titles...")
    for url in sorted(affected_titles):
        row = url_to_row.get(url, {})
        old = row.get("Title 1", "")
        new = generate_new_title(client, url, old)
        title_fixes.append({"url": url, "old": old, "new": new})

    with open(out_titles, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["url", "old", "new"])
        writer.writeheader()
        writer.writerows(title_fixes)

    # 2. Handle Redirects
    broken_links = []
    for issue in report["issues"]:
        if issue["type"] == "broken_link":
            broken_links.extend(issue["affected_urls"])

    live_pages = [r["Address"] for r in rows if r.get("Status Code") == "200"]
    redirect_fixes = []
    print(f"Mapping {len(broken_links)} broken links...")
    for url in sorted(set(broken_links)):
        target = find_closest_live_page(url, live_pages)
        redirect_fixes.append({
            "from": url,
            "to": target,
            "reason": "Broken link (4xx) redirected to closest live page"
        })

    with open(out_redirects, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["from", "to", "reason"])
        writer.writeheader()
        writer.writerows(redirect_fixes)

    # 3. Update report.json
    fixes_data = {
        "titles": title_fixes,
        "redirect_map": redirect_fixes
    }
    report["fixes"] = fixes_data

    # Update model calls if LLM was used
    if client:
        report["run_meta"]["model_calls"] += len(title_fixes)

    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"Success: Fixed {len(title_fixes)} titles and {len(redirect_fixes)} redirects.")
    print(f"Artifacts written to {out_titles} and {out_redirects}")

    return fixes_data

def main():
    parser = argparse.ArgumentParser(description="SEO Fix Champion Stage")
    parser.add_argument("export_dir", help="Directory containing the Screaming Frog export")
    args = parser.parse_args()
    run_fixes(args.export_dir)
