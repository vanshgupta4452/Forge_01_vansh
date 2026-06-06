"""
detector.py — HIGH ACCURACY SEO RULE ENGINE (Forge Sprint optimized)

Upgrades over starter:
- Normalization layer (critical for duplicate correctness)
- Proper redirect graph traversal (chain + loop detection)
- Stronger grouping logic (indexable-only consistency)
- Better edge-case handling (SF export inconsistencies)
- Reduced false positives
"""

from __future__ import annotations
import csv
import os
from collections import defaultdict, deque


# ----------------------------
# IO
# ----------------------------

def load_rows(export_dir: str) -> list[dict]:
    path = os.path.join(export_dir, "internal_all.csv")
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


# ----------------------------
# SAFE CASTS
# ----------------------------

def _int(v, default=0):
    try:
        return int(float(str(v).strip()))
    except:
        return default


def _float(v, default=0.0):
    try:
        return float(str(v).strip())
    except:
        return default


# ----------------------------
# NORMALIZATION (VERY IMPORTANT)
# ----------------------------

def norm(x: str) -> str:
    return (x or "").strip().lower()


# ----------------------------
# CORE FILTERS
# ----------------------------

def is_html(r):
    return "text/html" in norm(r.get("Content Type"))


def is_200(r):
    return _int(r.get("Status Code")) == 200


def indexable(r):
    return norm(r.get("Indexability")) == "indexable"


def is_indexable_200(r):
    return is_html(r) and is_200(r) and indexable(r)


# ----------------------------
# ISSUE ADDER
# ----------------------------

def add(issues, t, sev, urls, explanation):
    urls = sorted(set(urls))
    if urls:
        issues.append({
            "type": t,
            "severity": sev,
            "affected_urls": urls,
            "count": len(urls),
            "explanation": explanation
        })


# ----------------------------
# REDIRECT GRAPH ANALYSIS
# ----------------------------

def build_redirect_graph(rows):
    graph = {}
    status = {}

    for r in rows:
        code = _int(r.get("Status Code"))
        url = r.get("Address")

        status[url] = code

        if 300 <= code <= 399:
            target = r.get("Redirect URL")
            if target:
                graph[url] = target

    return graph, status


def detect_redirect_issues(rows, issues):
    graph, status = build_redirect_graph(rows)

    visited_global = set()

    def trace(url):
        visited = set()
        path = []

        while url in graph:
            if url in visited:
                return ("loop", path)
            visited.add(url)
            path.append(url)
            url = graph[url]

        return ("chain", path)

    chains = []
    loops = []

    for url in graph:
        if url in visited_global:
            continue

        kind, path = trace(url)
        visited_global.update(path)

        if kind == "loop":
            loops.extend(path)
        elif len(path) > 1:
            chains.extend(path)

    add(issues, "redirect_chain", "High", chains,
        "Multi-step redirect chain detected.")

    add(issues, "redirect_loop", "High", loops,
        "Redirect loop detected.")


# ----------------------------
# DETECTOR CORE
# ----------------------------

def detect(rows: list[dict]) -> list[dict]:
    issues = []

    # ---------------- FILTERS ----------------
    html = [r for r in rows if is_html(r)]
    idx200 = [r for r in html if is_200(r) and indexable(r)]
    html_200 = [r for r in html if is_200(r)]

    # ---------------- TITLES ----------------

    add(
        issues,
        "missing_title",
        "High",
        [r["Address"] for r in idx200 if not norm(r.get("Title 1"))],
        "Indexable 200 pages missing titles."
    )

    title_map = defaultdict(list)
    for r in idx200:
        t = norm(r.get("Title 1"))
        if t:
            title_map[t].append(r["Address"])

    dup_titles = [u for urls in title_map.values() if len(urls) > 1 for u in urls]

    add(
        issues,
        "duplicate_title",
        "High",
        dup_titles,
        "Duplicate titles across indexable pages."
    )

    add(
        issues,
        "title_too_long",
        "Medium",
        [r["Address"] for r in idx200
         if _int(r.get("Title 1 Length")) > 60 or _int(r.get("Title 1 Pixel Width")) > 561],
        "Titles exceeding SEO limits."
    )

    add(
        issues,
        "title_too_short",
        "Low",
        [r["Address"] for r in idx200
         if 0 < _int(r.get("Title 1 Length")) < 30],
        "Titles too short for SEO."
    )

    # ---------------- META ----------------

    add(
        issues,
        "missing_meta_description",
        "Medium",
        [r["Address"] for r in idx200 if not norm(r.get("Meta Description 1"))],
        "Missing meta descriptions."
    )

    meta_map = defaultdict(list)
    for r in idx200:
        m = norm(r.get("Meta Description 1"))
        if m:
            meta_map[m].append(r["Address"])

    dup_meta = [u for urls in meta_map.values() if len(urls) > 1 for u in urls]

    add(
        issues,
        "duplicate_meta_description",
        "Medium",
        dup_meta,
        "Duplicate meta descriptions."
    )

    add(
        issues,
        "meta_description_too_long",
        "Low",
        [r["Address"] for r in idx200 if _int(r.get("Meta Description 1 Length")) > 155],
        "Meta description too long."
    )

    # ---------------- H1 ----------------

    add(
        issues,
        "missing_h1",
        "Medium",
        [r["Address"] for r in html_200 if not norm(r.get("H1-1"))],
        "Missing H1 tags on 200 pages."
    )

    h1_map = defaultdict(list)
    for r in idx200:
        h = norm(r.get("H1-1"))
        if h:
            h1_map[h].append(r["Address"])

    dup_h1 = [u for urls in h1_map.values() if len(urls) > 1 for u in urls]

    add(
        issues,
        "duplicate_h1",
        "Low",
        dup_h1,
        "Duplicate H1 across pages."
    )

    # ---------------- RESPONSE CODES ----------------

    add(
        issues,
        "broken_link",
        "High",
        [r["Address"] for r in rows if 400 <= _int(r.get("Status Code")) <= 499],
        "Client error pages (4xx)."
    )

    add(
        issues,
        "server_error",
        "High",
        [r["Address"] for r in rows if 500 <= _int(r.get("Status Code")) <= 599],
        "Server error pages (5xx)."
    )

    add(
        issues,
        "redirect",
        "Medium",
        [r["Address"] for r in rows if 300 <= _int(r.get("Status Code")) <= 399],
        "Redirecting URLs."
    )

    # ---------------- REDIRECT CHAINS / LOOPS ----------------
    detect_redirect_issues(rows, issues)

    # ---------------- ORPHANS ----------------

    add(
        issues,
        "orphan_page",
        "Medium",
        [r["Address"] for r in idx200 if _int(r.get("Inlinks")) == 0],
        "Indexable pages with no internal links."
    )

    # ---------------- NON INDEXABLE BUT LINKED ----------------

    add(
        issues,
        "non_indexable_but_linked",
        "Medium",
        [r["Address"] for r in rows
         if norm(r.get("Indexability")) == "non-indexable" and _int(r.get("Inlinks")) > 0],
        "Non-indexable pages still receiving internal links."
    )

    # ---------------- THIN CONTENT ----------------

    add(
        issues,
        "thin_content",
        "Low",
        [r["Address"] for r in idx200 if _int(r.get("Word Count")) < 200],
        "Low word count pages."
    )

    # ---------------- IMAGES ----------------

    if rows and "Alt Text" in rows[0]:
        add(
            issues,
            "missing_image_alt",
            "Medium",
            [r["Address"] for r in rows
             if "image" in norm(r.get("Content Type")) and not norm(r.get("Alt Text"))],
            "Images missing alt text."
        )

    # ---------------- SLOW PAGES ----------------

    add(
        issues,
        "slow_page",
        "Low",
        [r["Address"] for r in rows if _float(r.get("Response Time")) > 1.0],
        "Slow response pages."
    )

    return issues


# ----------------------------
# SUMMARY
# ----------------------------

def summarize(issues: list[dict]) -> dict:
    from collections import defaultdict

    by = defaultdict(int)
    for i in issues:
        by[i["severity"]] += 1

    return {
        "total_issues": len(issues),
        "by_severity": {
            "High": by["High"],
            "Medium": by["Medium"],
            "Low": by["Low"]
        }
    }


# ----------------------------
# CLI
# ----------------------------

if __name__ == "__main__":
    import sys, json

    d = sys.argv[1] if len(sys.argv) > 1 else "../sample-export"
    rows = load_rows(d)

    issues = detect(rows)

    print(f"Loaded {len(rows)} rows")
    print(json.dumps(summarize(issues), indent=2))

    for i in issues:
        print(f"[{i['severity']}] {i['type']} -> {i['count']}")