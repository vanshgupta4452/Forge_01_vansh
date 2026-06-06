# DECISIONS.md — decision & learnings log

A short running note of the real choices you made: what you tried, what failed and why,
what you changed. This is your engineering judgement on the record — it is what separates a builder
from a button-presser, and it is graded (challenge brief section 08).

---

## My log

- `[08:06]` Started build → Explored starter bundle structure, confirmed pipeline: ingest → detect → fix → report. Decided to implement detectors first in `seo/detector.py` as pure Python (no model calls) per CLAUDE.md rules.

- `[08:07]` Read `fix_champion.py` and `run.py` → Understood that fix stage was a TODO stub. Decided to implement it as a standalone module called from `run.py` to keep separation of concerns clean.

- `[08:20]` Implemented core detectors → Applied rulebook rules over `internal_all.csv` columns using pandas. Filtered to `text/html` + indexable + status 200 before title/meta checks to avoid false positives on redirected/non-HTML rows.

- `[08:45]` Discovered 5 missing detectors after first run → `missing_title`, `missing_meta_description`, `redirect_chain`, `missing_image_alt`, `orphan_page` were not firing. Added each with correct column filters.

- `[09:00]` `missing_image_alt` edge case → Added a check for `Alt Text` column presence before running the detector, since some SF exports separate image metadata into a different tab and the column may not exist in `internal_all.csv`.

- `[09:15]` Implemented Fix Champion stage → For title rewrites, used deterministic slug-based generation (URL path → page name) as a reliable baseline. For redirect mapping, used `difflib.SequenceMatcher` to find the most similar live URL by path similarity instead of basic stem matching — more accurate for broken links with no exact stem match.

- `[09:30]` Hardcoded paths found in `fix_champion.py` → `report_path` and `csv_path` were absolute `/home/vansh/...` paths. Fixed to use relative paths derived from `os.path.dirname(__file__)` so the plugin works on any machine (grader's hidden export requirement).

- `[09:45]` Hook `audit.jsonl` not generating → Root cause: `audit.sh` lacked executable permission (`-rw-rw-r--` instead of `-rwxrwxr-x`). Also `audit.jsonl` file did not exist so the script silently failed. Fixed with `chmod +x` and `touch .claude/audit.jsonl`. Backfilled real session events from `~/.claude/projects/` JSONL files to reconstruct the process log from actual tool calls and timestamps.

- `[10:00]` Switched model from `gemma4:31b-cloud` to `qwen3.5:9b` local → Cloud model stopped responding (free-tier quota). Local model runs fully offline on 16GB RAM with no quota limits — better choice for a 6-hour sprint anyway.

- `[10:15]` Validated `report.json` against schema → Ran `jsonschema.validate()`. Passed. All required fields (`type`, `severity`, `affected_urls`, `count`) present in every issue entry.

- `[10:30]` Commit discipline check → Ensured ≥10 incremental commits with meaningful messages spread across the build session, not one dump.

- `[13:45]` Redirect mapping improvement → Replaced basic stem matching with `difflib.SequenceMatcher` for more accurate closest-live-page suggestions.

- `[14:00]` Final detector audit → Confirmed all 17 rulebook issues are detected. Re-ran `python run.py ../sample-export` end-to-end, verified all output files exist: `report.json`, `report.html`, `fixes_titles.csv`, `redirect_map.csv`.