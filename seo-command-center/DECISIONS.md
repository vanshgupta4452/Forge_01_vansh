# DECISIONS.md — decision & learnings log

A short running note of the real choices you made: what you tried, what failed and why,
what you changed. This is your engineering judgement on the record — it is what separates a builder
from a button-presser, and it is graded (challenge brief section 08).

Append a 1–2 line entry whenever you make a real decision or hit/fix a wall. Add a timestamp.

Format:
`[HH:MM] <decision or problem> → <what you did and why>`

---

## My log
`[11:00]` Started build → Ran prompt #1: read full repo to understand architecture before touching any code. Confirmed pipeline: ingest → detect → fix → report. Decided to audit gaps first, implement later.

- `[11:10]` Created detector coverage table → Ran prompt #2: mapped every rulebook rule against `detector.py` line by line. Found ~10 detectors missing. This table became the implementation checklist for the rest of the build.

- `[11:20]` Implemented `missing_title` first → Ran prompt #3: started with one detector to validate the pattern (add to detect loop → appears in report.json) before doing bulk implementation. Confirmed it worked end-to-end.

- `[11:30]` Deep inspection of detector.py → Ran prompt #4: verified line numbers and confirmed which issues were missing from report.json output, not just from detection logic. Some detectors existed but were not being serialized.

- `[11:40]` Batch implemented 3 metadata detectors → Ran prompt #5: added `title_too_short`, `missing_meta_description`, `duplicate_meta_description` together since they share the same column filters and coding pattern.

- `[12:00]` Full rulebook compliance in one pass → Ran prompt #6: implemented all remaining detectors in a single consolidated change. Filtered to `text/html` + indexable + status 200 before title/meta checks to avoid false positives. Used exact rulebook thresholds (561px, 60 chars, 155 chars, etc.).

- `[12:15]` Implemented Fix Champion stage → Ran prompt #7: for title rewrites used deterministic slug-based generation (URL path → page name). For redirect mapping used `difflib.SequenceMatcher` instead of basic stem matching — more accurate for broken links with no exact stem match. Wrote `fixes_titles.csv` and `redirect_map.csv`.

- `[12:30]` Hardcoded paths found in `fix_champion.py` → `report_path` and `csv_path` were absolute `/home/vansh/...` paths. Fixed to use relative paths via `os.path.dirname(__file__)` so plugin works on grader's hidden export.

- `[12:45]` 5 detectors still missing after audit → Ran prompt #8: `missing_title`, `missing_meta_description`, `redirect_chain`, `missing_image_alt`, `orphan_page` were not in report.json output. Added all 5 with correct column filters. `missing_image_alt` needed a column existence check since some SF exports don't include `Alt Text` in `internal_all.csv`.

- `[13:00]` Switched model mid-sprint → `gemma4:31b-cloud` stopped responding (free-tier quota exhausted). Switched to `qwen3.5:9b` local model. Runs fully offline on 16GB RAM, no quota limits — better for a 6-hour sprint.

- `[13:15]` Hook `audit.jsonl` not generating → Root cause: `audit.sh` lacked executable permission (`-rw-rw-r--`). Also `audit.jsonl` file did not exist so the script silently failed with no error visible (hooks run `async: true`). Fixed with `chmod +x .claude/hooks/audit.sh` and `touch .claude/audit.jsonl`. **Note: since hooks were not firing during the session, audit entries were manually backfilled by extracting real tool calls, prompts, and timestamps from `~/.claude/projects/` session JSONL files and converting them to audit format. The underlying work is real and matches git history and session transcripts.**

- `[13:30]` Validated `report.json` against schema → Ran `jsonschema.validate()` against `report.schema.json`. Passed. All required fields (`type`, `severity`, `affected_urls`, `count`) present in every issue entry.

- `[13:45]` Process files compliance → Ran prompt #9: checked all required files exist — `audit.jsonl`, `agent-log.md`, `CLAUDE.md`, `PROMPTS.md`, `DECISIONS.md`. Exported session transcript via `scripts/export-transcript.sh`.

- `[14:00]` Commit discipline check → Verified ≥10 incremental commits with meaningful messages spread across the build. Each working step committed separately.

- `[14:10]` Final end-to-end test → Re-ran `python run.py ../sample-export`. All 17 rulebook issues detected. All output files present: `report.json`, `report.html`, `fixes_titles.csv`, `redirect_map.csv`. Schema valid.