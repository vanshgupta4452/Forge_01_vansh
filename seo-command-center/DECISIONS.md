# DECISIONS.md — decision & learnings log

A short running note of the real choices you made: what you tried, what failed and why,
what you changed. This is your engineering judgement on the record — it is what separates a builder
from a button-presser, and it is graded (challenge brief section 08).

Append a 1–2 line entry whenever you make a real decision or hit/fix a wall. Add a timestamp.

Format:
`[HH:MM] <decision or problem> → <what you did and why>`

---

## My log
- `[13:45]` Implemented Fix Champion stage → Used `difflib.SequenceMatcher` for redirect mapping to find the most similar live URL instead of basic stem matching, improving accuracy for broken links.
- `[14:00]` Added missing detectors → Implemented `missing_image_alt` with a check for the `Alt Text` column presence to avoid false positives in exports that separate image metadata.
