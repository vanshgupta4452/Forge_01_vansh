# PROMPTS.md — my key prompts log

Keep the handful of prompts that actually moved the build. Not every message — the ones that
mattered: the system/sub-agent prompts, the ones you iterated on, the "this finally worked"
moment. This shows how you direct an AI, which is graded (challenge brief section 08).

Format per entry:
- **Prompt** (paste it)
- **For:** what you were trying to do
- **Revised?** did you have to change it, and why

---

## My prompts

- **Prompt:** "Implement the fix champion stage: 1. For all duplicate/missing/too-long/too-short titles, use the LLM to rewrite them within 30-60 chars / 561px limit 2. For broken links (4xx), build a redirect map suggesting the closest live page 3. Write fix artifacts: outputs/fixes_titles.csv and outputs/redirect_map.csv 4. Populate the fixes block in report.json"
- **For:** Implementing the automated fix generation pipeline.
- **Revised?** No.

- **Prompt:** "Add these missing detectors to the audit pipeline: - missing_title: empty Title 1 on indexable 200 pages - missing_meta_description: empty Meta Description 1 on indexable 200 pages - redirect_chain: URL redirects to another URL that also redirects - missing_image_alt: image content-type rows with empty alt text - orphan_page: Inlinks = 0 on indexable 200 pages"
- **For:** Expanding the SEO audit coverage.
- **Revised?** No.
