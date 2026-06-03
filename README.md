# Business Analysis Learning Agent Skill

> A learning-oriented AI Agent Skill that turns business datasets into beginner-friendly Excel, PDF, and presentation-ready insights.
>
> 面向商业初学者的 AI 数据分析 Skill：自动生成 Excel、PDF、审计日志，并解释指标逻辑与商业洞察。

A platform-agnostic Agent Skill for learning-oriented business data analysis. This skill helps an AI agent teach business beginners how to think about data — not just produce charts and summaries.

## Why This Project

Business beginners often face a gap: they have data (CSV exports, Excel reports, CRM dumps) but don't know how to go from raw numbers to actionable insights. Existing tools either require advanced skills (Python, SQL, statistics) or produce black-box results without explanation.

This project bridges that gap:

- **For learners**: the Agent explains what each metric means, why a method was chosen, what the results CANNOT prove, and how to reuse the thinking next time — in beginner-friendly Chinese.
- **For portfolio builders**: every run produces professional Excel + PDF + audit log deliverables that demonstrate analysis capability.
- **For educators**: the 3-tier method layering (basic → advanced → expert) and structured teaching output rules provide a complete "learn by doing" (做中学) data analysis curriculum.

> **Teaching Layer (v0.10):** This Skill upgrades analysis output from "Finding → Suggestion" to "Finding → Method Explanation → Metric Explanation → Business Interpretation → Risk Boundary → Learning Transfer." See `docs/methodology/teaching_output_rules.md`.

## What It Is

This skill combines a **Python/pandas automated analysis pipeline** with **agent-driven analysis reasoning**:

- Read CSV/Excel data
- Profile the dataset (row count, columns, missing values, duplicates)
- Infer field business meanings from naming patterns (130+ patterns)
- Match computable business metrics from a predefined registry (14 metrics)
- Execute basic descriptive analysis (grouped ranking, trend, distribution)
- Check data quality risks
- Generate Excel / PDF / audit log deliverables
- Optionally produce HTML presentation decks via agent workflow
- Explain analysis logic, metric definitions, and business insights in Chinese

### What It Is Not

- Not a machine learning platform — the Python pipeline does not contain ML models
- Not an automated modeling tool — the pipeline does not use scikit-learn, statsmodels, or Prophet
- Not a replacement for SPSS, Stata, or SAS
- Not an "auto data scientist" — the analysis logic is rule-driven and fully auditable

> **Note:** The Agent (LLM) may execute Tier 2 advanced methods (correlation, RFM, etc.) using available tools when data conditions are met and the user confirms. These are agent-driven, not pipeline-driven. See `SKILL.md` Section 5 for the 3-tier method layering.

## How It Works

```
CSV/Excel → Data Intake → Field Semantics → Metric Registry → Analysis Planner → HTML/PDF/Excel/Audit
```

The analysis follows a fully deterministic, rule-driven pipeline:

1. **Data Intake** — `load_dataset()` / `load_folder()`, pandas reads CSV/Excel into DataFrame
2. **Data Profiling** — row count, columns, missing values, duplicates
3. **Field Semantics** — regex match 130+ naming patterns, map field names to business meanings
4. **Metric Matching** — match fields against 14 metric registry entries, compute CTR/CPC/margin if fields exist
5. **Quality Check** — negative values, zero rates, missing rates
6. **Ranking Analysis** — `groupby().agg(["sum","mean","count"])`, top/bottom segments
7. **Trend Analysis** — `dt.to_period("M")` → groupby + sum, month-over-month changes
8. **Distribution** — `describe()`, mean, median, std, quartiles
9. **Thinking Models** — 5 fixed templates with parameterized evidence
10. **Report Schema** — unified dict consumed by all renderers
11. **Render** — Excel (.xlsx), designed HTML report (.html), and PDF (.pdf)
12. **Audit Log** — JSON recording what ran, matched, skipped, and why

Each step maps to a specific module in `scripts/core/` or `scripts/renderers/`. See `docs/methodology/` for detailed documentation.

### PDF Rendering

PDF output is generated from a designed HTML/CSS business report first, then exported with WeasyPrint or Playwright's browser PDF engine. The older ReportLab renderer is kept as the final fallback if HTML-to-PDF export is unavailable. This keeps the report readable, avoids forced page breaks after every section, and makes layout tuning possible in the generated `*_report.html` file.

## Demo Outputs

The `sample_outputs/final_demo/` directory contains complete example outputs you can browse without running the tool:

| Demo | Contents | Description |
|------|----------|-------------|
| `final_demo/retail_demo/` | Excel + PDF + audit log | Retail sales analysis (12 records, 3 regions, 3 categories) |
| `final_demo/` (root) | Excel + PDF + PPTX | SaaS subscription churn analysis (multi-table merge) |

Each demo includes:
- `*_analysis.xlsx` — data tables, charts, and KPI dashboard
- `*_report.html` — designed teaching report for visual review and layout tuning
- `*_report.pdf` — PDF exported from the HTML report, with ReportLab fallback if needed
- `*_audit_log.json` — full audit trail of executed/skipped/recommended methods

See `sample_outputs/README.md` for details.

## Project Structure

```
├── README.md
├── QUICKSTART.md
├── SKILL.md                         platform-agnostic agent instructions
├── AGENT_INSTRUCTIONS.md            standalone instructions for non-Claude agents
├── requirements.txt
├── scripts/
│   ├── run_analysis.py              universal entry point (CLI)
│   ├── core/                        analysis runtime core (data intake, semantics, metrics, planner)
│   ├── renderers/                   output renderers (Excel, HTML/CSS→PDF)
│   ├── legacy/                      historical validation scripts (v0.1–v0.5; not part of main pipeline)
│   └── README.md
├── templates/                       agent reading: teaching & report templates
├── examples/                        agent/user reference examples
├── test_cases/                      sample datasets for testing
├── docs/
│   ├── methodology/                 detailed methodology documentation
│   ├── archive/                     archived docs and historical outputs
│
├── sample_outputs/                  GitHub showcase samples (not runtime)
├── vendor/agent_presentation_skills/  built-in presentation design dependencies (Guizang A/B, Design DNA)
├── .claude/                         optional Claude Code adapter
└── LICENSE
```

## Quick Start

### Prerequisites

- Python 3.9+
- `pip install -r requirements.txt`

### Run on a Single CSV

```bash
python3 scripts/run_analysis.py \
  --input "/path/to/your/data.csv" \
  --mode beginner_summary \
  --output-dir ~/Desktop/my_analysis
```

### Run on a Folder of Multiple CSVs

```bash
python3 scripts/run_analysis.py \
  --input "/path/to/data/folder/" \
  --mode audit_report \
  --output-dir ~/Desktop/multi_table_analysis
```

### Smoke Test (verify everything works)

```bash
python3 scripts/run_analysis.py \
  --input test_cases/sample_retail_sales.csv \
  --mode beginner_summary \
  --output-dir /tmp/balearn_smoke_test
```

Output files per run:

| File | Description |
|------|-------------|
| `*_analysis.xlsx` | Excel workbook with tables, charts, and dashboard |
| `*_report.html` | Designed HTML teaching report for browser review and PDF layout |
| `*_report.pdf` | PDF report exported from the HTML/CSS report |
| `*_audit_log.json` | JSON audit log of executed/skipped/recommended methods |

### Available Modes

| Mode | Use Case |
|------|----------|
| `beginner_summary` | First-time users, short friendly output |
| `standard_report` | Balance of explanation and readability |
| `audit_report` | Full detailed output for portfolio or review |

### Language

User-facing outputs default to **Chinese**. English or bilingual output is available through the agent workflow (not yet implemented as a CLI flag — see `SKILL.md` for agent-driven language switching).

## Agent Compatibility

This project is designed as a **platform-agnostic Agent Skill**:

- Claude Code (via `.claude/` adapter)
- Claude desktop/web (with file analysis)
- ChatGPT (with data analysis tools)
- Gemini or other agents that support instruction files

**Claude Code users** can run `/balearn` after opening this repository.

**Other agents** should use `AGENT_INSTRUCTIONS.md` as the starting prompt.

## Presentation Generation

The recommended way to get a presentation is through the **interactive agent workflow** (SKILL.md Step 9):

1. Analysis completes → user gets Excel + PDF
2. Agent asks whether to generate a presentation
3. If yes → choose from 2 styles:
   - **Guizang A (Editorial Magazine)** — two-page flipping HTML, WebGL backgrounds
   - **Guizang B (Swiss Typographic)** — minimal grid, strong hierarchy
4. Agent generates a standalone HTML deck

Presentation templates are bundled in `vendor/agent_presentation_skills/`.

Presentations are **Agent-only deliverables**. The universal CLI does not generate PPTX files or provide a `--ppt` shortcut. This guarantees that every presentation is created after the Agent reads the selected bundled presentation Skill and follows its design and QA rules.

## Use Cases

- Marketing campaign analysis
- Retail sales analysis
- Customer churn analysis
- Product performance analysis
- Financial metrics analysis
- Multi-table business data integration

## Who It Is For

- Business students learning data analysis
- Management, marketing, and operations beginners
- Users who need business interpretation, not just charts or code
- Anyone building a portfolio of business analysis work

## Design Principles

- Analysis is also learning — explain why before how
- Connect data fields to business questions
- Separate evidence, interpretation, and assumptions
- Keep beginner users in mind
- Deliver professional-quality Excel and PDF outputs

## Highlights

- **Platform-agnostic Agent Skill** — works with Claude Code, ChatGPT, Gemini, or any agent that reads instruction files
- **Beginner-friendly business language** — metrics, methods, and findings are explained in plain Chinese (English on request)
- **Fully auditable pipeline** — every step is recorded in a JSON audit log: what ran, what was skipped, and why
- **Multi-table intelligence** — detects join keys, classifies relationships, and safely merges related datasets
- **Professional deliverables** — Excel (.xlsx) with KPI dashboard, designed HTML report, PDF (.pdf) export, JSON audit log, and optional PPTX/HTML presentation deck
- **3-tier learning path** — built-in method layering from basic descriptive stats through advanced analysis, all conditional on data readiness

## Limitations

- **Not an ML platform** — the Python pipeline is rule-driven and does not contain machine learning models
- **Not a causal inference tool** — identifies patterns and associations, not causation
- **Limited statistical depth** — advanced methods (regression, time-series forecasting, clustering) require agent involvement and user confirmation
- **CSV/Excel only** — does not connect to databases, APIs, or cloud storage
- **In-memory processing** — very large datasets (>1M rows) may exhaust available RAM
- **Field semantics via naming patterns** — non-English or non-standard field names may not be recognized

## License

The main project is licensed under MIT. See `LICENSE`.

Bundled presentation Agent Skills retain their original licenses, including
the GNU AGPL-3.0 licensed `guizang-ppt-skill`. See
`THIRD_PARTY_NOTICES.md` for details.
