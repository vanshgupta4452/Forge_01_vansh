# PROMPTS.md — Key Prompts Log

This file contains only the prompts that meaningfully contributed to building the SEO Command Center.
Each entry captures intent, context, and iteration behavior for evaluation (process score).

---

## 1

- **Prompt:** "Read the entire repository.

Explain:

1. Current execution flow  
2. Which files are entry points  
3. Which SEO detectors are already implemented  
4. Which rulebook rules are missing  
5. Create a step-by-step implementation plan prioritized for scoring  

Do not modify any code."

- **For:** Understanding full project architecture, execution flow, and identifying missing SEO rule implementations before development.
- **Revised?** No

---

## 2

- **Prompt:** "Read the entire repository.

Focus on:
- seo/detector.py
- run.py
- mcp/server.py

Create a table:

Rulebook Issue | Implemented | Function Name | Missing Logic

Do not modify code.
Do not write code.
Only produce an implementation checklist."

- **For:** Mapping existing detector implementation against rulebook requirements to identify coverage gaps.
- **Revised?** No

---

## 3

- **Prompt:** "Implement missing_title detection according to rulebook.md.

Requirements:
- Follow existing coding style.
- Add detector to report output.
- Do not modify unrelated files.
- Explain changes before making them."

- **For:** Implementing first deterministic SEO rule (missing title detection) in the pipeline.
- **Revised?** No

---

## 4

- **Prompt:** "Read detector.py completely.

Create a table:

Rulebook Issue | Implemented | Line Numbers | Included in report.json output

For every missing issue:
- Show exact rulebook requirement
- Show why it is currently missing

Do not modify code."

- **For:** Deep inspection of detector implementation and verifying alignment with report output schema.
- **Revised?** No

---

## 5

- **Prompt:** "Implement the following detectors ONLY:

1. title_too_short  
2. missing_meta_description  
3. duplicate_meta_description  

Requirements:
- Follow existing detector.py style.
- Add them to the detect() loop.
- Ensure they appear in report.json output.
- Explain changes before editing."

- **For:** Expanding SEO detector coverage with core metadata-related rules.
- **Revised?** No

---

## 6

- **Prompt:** "Implement ALL missing rulebook detectors in a single change:

- title_too_short  
- missing_meta_description  
- duplicate_meta_description  
- meta_description_too_long  
- missing_h1  
- duplicate_h1  
- thin_content  
- non_indexable_but_linked  
- slow_page  
- redirect_chain  

Requirements:
1. Follow existing coding style and architecture.
2. Add every detector to detect() flow.
3. Ensure every detector appears in report.json output.
4. Reuse helper functions where possible.
5. Do not modify dashboard, MCP server, HTML templates, or unrelated files.
6. Use exact thresholds from rulebook.md.
7. Explain redirect_chain detection strategy before implementation.
8. Provide:
   - modified files
   - detectors added
   - coverage improvement summary
9. Validate missing columns if any rule cannot be implemented.
10. Run checks/tests if available.
"

- **For:** Full rulebook compliance implementation of SEO detection engine in one consolidated update.
- **Revised?** No

---

## 7

- **Prompt:** "Implement the fix champion stage:
1. Rewrite all duplicate/missing/invalid titles using LLM within 30–60 chars / 561px limit
2. Build redirect map for 4xx broken links using best-match live pages
3. Generate outputs/fixes_titles.csv and outputs/redirect_map.csv
4. Populate fixes block in report.json"

- **For:** Implementing AI-assisted fix generation system for SEO issues (titles + redirects).
- **Revised?** No

---

## 8

- **Prompt:** "Add these missing detectors to the audit pipeline:
- missing_title: empty Title 1 on indexable 200 pages
- missing_meta_description: empty Meta Description 1 on indexable 200 pages
- redirect_chain: URL redirects to another URL that also redirects
- missing_image_alt: image rows with empty alt text
- orphan_page: Inlinks = 0 on indexable 200 pages"

- **For:** Expanding deterministic SEO coverage to fully align pipeline with rulebook requirements.
- **Revised?** No

---

## 9

- **Prompt:** "Your repo must contain these process, context and memory files... (audit.jsonl, agent-log.md, CLAUDE.md, PROMPTS.md, DECISIONS.md requirements)"

- **For:** Ensuring compliance with evaluation process tracking and auditability requirements for scoring.
- **Revised?** No

---

## 10

- **Prompt:** "in prompts.md add all the history of yours for this folder"

- **For:** Attempting to consolidate full interaction history into a structured process log.
- **Revised?** No

---

## 11

- **Prompt:** "[Request interrupted by user for tool use] you have 31 prompts in history add all that prompt in prompt.md"

- **For:** Requesting full reconstruction of session prompt history into PROMPTS.md for evaluation completeness.
- **Revised?** No