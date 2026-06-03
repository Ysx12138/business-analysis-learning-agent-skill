# Universal Runner Design

> **Implementation status:**
> - v0.6/v0.6.2: single-table + multi-table universal analysis implemented
> - v0.7: presentation renderer / HTML deck generation implemented
> - Section sections below describe the **current** architecture, not a future plan.
> - Sections marked **[Planned]** are still under consideration.

This document describes the architecture of the reusable analysis runner.

## Goal

The universal runner accepts any CSV/Excel dataset (single file or folder) and produces learning-oriented business analysis deliverables without writing a new custom script for each dataset.

The runner preserves the core skill behavior:

- ask for output mode before analysis
- default user-facing outputs to Chinese
- inspect data quality before conclusions
- infer business meaning from fields
- detect relationships between multiple tables
- compute metrics automatically from a registry
- explain metrics and methods for beginners
- generate Excel, PDF, and optional HTML presentation deliverables

## Why Not Dataset-Specific Scripts

The earlier v0.5 validation proved the skill works across five business scenarios (marketing, SaaS churn, retail operations, product reviews, financial analysis). But each scenario had its own end-to-end script. This approach is useful for validation but not scalable.

The reusable runner solves this by separating:
- **analysis logic** (core modules)
- **output rendering** (renderers)
- **agent instructions** (SKILL.md / AGENT_INSTRUCTIONS.md)

## Current Architecture

```
scripts/
├── run_analysis.py          universal entry point
├── core/
│   ├── data_intake.py       load CSV/Excel, profile statistics
│   ├── field_semantics.py   infer field business meaning (100+ patterns)
│   ├── metric_registry.py   14 base metrics + derived metrics, auto-detect fields
│   ├── analysis_planner.py  plan ranking/trend/distribution analyses
│   ├── relationship_detector.py   multi-table join detection + plan
│   └── result_schema.py     unified result schema (v0.2.0)
├── renderers/
│   ├── excel_renderer.py         generic Excel renderer (openpyxl)
│   ├── html_report_renderer.py   HTML/CSS report → WeasyPrint/Playwright → PDF (primary path)
│   └── pdf_renderer.py           ReportLab PDF renderer (fallback only)
└── profiles/                [planned] domain-specific profiles
```

## Runner Flow

### 1. Data Intake

**Implemented.** `data_intake.py` handles:

- single CSV file (`load_dataset`)
- single Excel file
- folder of multiple CSV/Excel files (`load_folder` in `relationship_detector.py`)

Output includes row/column counts, field names and types, missing value summary, duplicate summary, and potential key/date/money/category/text field detection.

### 2. Field Semantics Mapping

**Implemented.** `field_semantics.py` infers field meaning using a pattern registry with 100+ semantic patterns across 16 business domains:

| Field | Inferred Meaning | Evidence |
|---|---|---|
| `customer_id` | customer identifier | naming convention |
| `order_date` | transaction date | naming + type |
| `Spent` | advertising spend | domain keyword match |
| `Total_Conversion` | conversion count | domain keyword match |

Low-confidence fields are surfaced in the field_semantics table with lower confidence scores.

### 3. Business Metric Definition

**Implemented.** `metric_registry.py` provides 14 base metrics plus derived metrics (CTR, CPC, profit margin, debt ratio, conversion rate), grouped by business domain (general, marketing, financial, retail, SaaS, review, support, operations).

Each metric includes:
- formula (e.g., CTR = clicks / impressions)
- required fields
- business meaning
- limitation

Metrics auto-match to dataset fields. Derived metrics (calculated from existing fields) are detected separately.

### 4. Multi-Table Relationship Detection

**Implemented.** `relationship_detector.py` handles:

- **Single-column key detection:** naming convention (`_id`, `_key` suffix) + data characteristics (unique ratio, overlap)
- **Compound key detection:** column pairs (e.g., Store + Date) when no single column is a good join key
- **Relationship type classification:** one-to-one, one-to-many, many-to-one, many-to-many based on unique ratios
- **Join plan generation:** greedy algorithm (ID-key-first, compound-key priority, each table at most once)
- **Join execution:** pandas merge with column conflict handling (table-name suffix), row explosion sanity check (>50x threshold)

### 5. Analysis Planner

**Implemented.** `analysis_planner.py` selects analysis modules based on detected fields:

- grouping + ranking (category + metric)
- trend analysis (date + metric)
- distribution analysis (numeric field)
- cross-analysis (two category dimensions)

Also generates:
- key findings (data evidence + business interpretation)
- thinking models (decomposition, segment divergence, proxy inference, constraint vs preference, leverage point)
- recommendations (actionable, tied to evidence)
- data quality risk checks

### 6. Standard Result Schema

**Implemented.** `result_schema.py` defines a unified dict format (v0.2.0) consumed by all three renderers:

```python
report = {
    "title": str,
    "dataset_overview": {...},
    "field_semantics": [...],
    "metric_glossary": [...],
    "key_findings": [...],
    "thinking_models": [...],
    "recommendations": [...],
    "tables": [...],
    "data_quality": {...},
    "beginner_notes": {...},
}
```

Every analysis module and every renderer uses this same schema. Dataset-specific scripts do not need custom rendering logic.

### 7. Deliverable Renderers

**Implemented.** Three renderers consume the result schema:

**Excel renderer** (`excel_renderer.py`):
- Overview sheet → field semantics → data quality → metric glossary → result sheets → dashboard
- Auto column width, number formatting, conditional bar charts
- KPI color blocks on dashboard page
- Safe sheet name truncation (25 chars for OpenPyXL compliance)

**PDF / HTML renderer** (`html_report_renderer.py`):
- Primary path: HTML/CSS business report → WeasyPrint or Playwright → PDF
- Also generates a browser-reviewable `*_report.html` file
- `pdf_renderer.py` (reportlab) is kept as a stable fallback when HTML-to-PDF export is unavailable
- Cover page → overview → semantics → data quality → findings → thinking models → metrics → tables → recommendations

**HTML deck generation** (v0.7, via agent workflow):
- Interactive style selection (Guizang A / Guizang B)
- Standalone HTML file, WebGL backgrounds, Motion One animations
- Mandatory Agent-only path: the Agent must read the selected bundled presentation Skill under `vendor/agent_presentation_skills/`
- The universal runner does not generate presentations or provide a PPT shortcut

## CLI Shape

**Implemented.** Current command:

```bash
python scripts/run_analysis.py \
  --input "/path/to/dataset_or_folder" \
  --mode beginner_summary \
  --output-dir ~/Desktop/my_analysis \
  --no-excel \
  --no-pdf
```

Required: `--input`, `--mode`, `--output-dir`.

Optional: `--title`, `--no-excel`, `--no-pdf`.

CLI behavior:
- Creates a timestamped subdirectory inside `--output-dir` (e.g., `~/Desktop/my_analysis/sample_retail_sales_2026-06-03_165757/`).
- This prevents silent overwrites when running the same dataset multiple times.
- The final output path is printed to console and recorded in the audit log.

Multi-table mode: pass a folder path to `--input`.

## Implementation Milestones

| Milestone | Status | Description |
|-----------|--------|-------------|
| v0.6: Generic single-table runner | ✅ Done | CSV/Excel input, profile, semantics, ranking/trend analysis, Excel + PDF |
| v0.6.2: Multi-table runner | ✅ Done | Folder input, relationship detection, join plan, compound keys, safe join |
| v0.7: Presentation workflow | ✅ Done | Interactive style selection, Guizang A/B HTML decks |
| Domain profiles | 📋 Planned | marketing, retail, SaaS profiles for deeper domain-specific analysis |
| CLI `--language` flag | 📋 Planned | Pending: currently language is set in the agent workflow, not CLI |
| `--domain` profile selection | 📋 Planned | Auto-select analysis modules based on domain |
| Web UI | 📋 Planned | Optional frontend for non-CLI users |

## Design Rule

The runner should not hide uncertainty.

If a field meaning, metric definition, or join relationship is uncertain, the runner should record the assumption and surface it instead of producing a confident but fragile conclusion.
