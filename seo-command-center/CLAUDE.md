# CLAUDE.md — SEO Command Center Project Memory

This file defines the operating context, constraints, and architecture for the Claude Code SEO Command Center plugin.

It is automatically loaded each session and serves as the **single source of truth for agent behavior**.

---

## 🎯 Project Goal

Build an autonomous SEO Command Center plugin that:

- Ingests Screaming Frog export (`internal_all.csv`)
- Detects SEO issues using deterministic rule engine (rulebook.md)
- Prioritizes issues by severity and impact
- Generates AI-assisted fixes (titles, meta descriptions, redirects)
- Runs a live dashboard at `http://localhost:7700`
- Outputs:
  - `outputs/report.json` (strict schema compliant)
  - `outputs/report.html` (client report)
  - optional fix artifacts (titles + redirect maps)

---

## ⚙️ Core Architecture

### 1. Skill Layer
- `SKILL.md` orchestrates full pipeline execution
- Defines workflow: ingest → detect → prioritize → fix → report

### 2. Deterministic Engine (CRITICAL)
- `seo/detector.py` handles ALL rule-based detection
- Must implement rulebook strictly using pandas / python logic
- No LLM usage for detection logic

### 3. MCP Server
- `mcp/server.py`
- Hosts:
  - live dashboard (port 7700)
  - runtime tools for pipeline execution

### 4. Fix Generator (LLM Layer)
- Only used for:
  - rewriting titles
  - rewriting meta descriptions
  - selecting redirect targets
- Must validate outputs before writing

---

## 🚨 Hard Constraints (DO NOT VIOLATE)

- Never send full dataset to the LLM
- Always filter:
  - `Content Type == text/html`
  - `Indexability == Indexable`
  before SEO checks
- Every issue must map to real URLs from dataset
- `report.json` must validate against `report.schema.json`
- Must work on unseen exports (no hardcoding sample data)

---

## 📊 SEO Detection Rules (High-Level)

Implement all rulebook checks including:

- missing_title
- duplicate_title
- title_length violations
- missing_meta_description
- duplicate_meta_description
- missing_h1
- duplicate_h1
- thin_content (<200 words)
- orphan_page (inlinks = 0)
- non_indexable_but_linked
- redirect_chain / loop
- 4xx broken links
- 5xx server errors
- slow pages (>1s response)

All detectors must be:
- deterministic
- traceable
- reproducible

---

## 📦 Output Contract

Must always generate:

### report.json
- schema-compliant
- includes:
  - issues[]
  - severity breakdown
  - fixes block
  - recommendations

### report.html
- client-facing summary
- issue prioritization

### fix artifacts (champion requirement)
- titles.csv
- redirect_map.csv

---

## 🔁 Execution Flow

1. Load CSV (`internal_all.csv`)
2. Clean + filter dataset
3. Run deterministic detectors
4. Aggregate + group issues
5. Compute severity scoring
6. Call LLM only for fix generation
7. Validate outputs
8. Write:
   - report.json
   - report.html
   - fix files
9. Stream updates to dashboard

---

## 📌 Engineering Principles

- Determinism > intelligence for detection
- LLM only for rewriting, never for classification
- Keep pipeline modular and testable
- Validate every output before writing
- Optimize for unseen dataset correctness

---

## 🧠 Known Edge Cases (updated during build)

- Redirected pages may still have missing titles → filter Status Code 200 first
- Non-indexable pages should be excluded from most checks
- Duplicate detection must exclude non-HTML pages
- Pixel width constraints must override character length when both exist

---

## 🏁 Success Criteria

The system is correct only if:

- Works on unseen Screaming Frog export
- report.json passes schema validation
- Issue detection matches rulebook precisely
- No hallucinated URLs or fake issues
- Dashboard reflects live pipeline state

---