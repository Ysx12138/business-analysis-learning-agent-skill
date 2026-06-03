# Quick Start

This guide helps you run your first business data analysis with this skill.

## Requirements

- Python 3.9+
- Install dependencies:

```bash
pip install -r requirements.txt
```

## Run Analysis on a Single CSV

```bash
python3 scripts/run_analysis.py \
  --input "/path/to/your/data.csv" \
  --mode beginner_summary \
  --output-dir ~/Desktop/my_analysis
```

That's it. Four files appear in a timestamped subdirectory under `~/Desktop/my_analysis/`:

| File | What it is |
|------|-----------|
| `*_analysis.xlsx` | Data tables + charts + dashboard |
| `*_report.html` | Designed teaching report for browser review and layout tuning |
| `*_report.pdf` | PDF exported from the HTML/CSS report |
| `*_audit_log.json` | Analysis audit record (what ran, what was skipped, why) |

## Run on a Folder of Multiple CSVs

If you have several related CSV files (e.g., sales + stores + products), point to the folder:

```bash
python3 scripts/run_analysis.py \
  --input "/path/to/data/folder/" \
  --mode audit_report \
  --output-dir ~/Desktop/multi_table_analysis
```

The tool automatically detects relationships between tables, finds join keys, and merges them into one analysis.

## Smoke Test (Verify Installation)

```bash
python3 scripts/run_analysis.py \
  --input test_cases/sample_retail_sales.csv \
  --mode beginner_summary \
  --output-dir /tmp/smoke_test
```

If this runs without errors and produces Excel, HTML, PDF, and audit log files, your installation is working.

## Choose Output Mode

| Mode | When to Use |
|------|-------------|
| `beginner_summary` | First time exploring a dataset — short and friendly |
| `standard_report` | Need a balanced report with key reasoning |
| `audit_report` | Portfolio, testing, or full quality review |

## Language

Default user-facing language is **Chinese**. English or bilingual output is available through the agent workflow — the CLI does not yet support a `--language` flag. When using an AI agent (see below), state your language preference at the start.

## Using with an AI Agent

**Claude Code** (in this repo):

```
/balearn
```

Then follow the prompts — the agent will ask for output mode and output folder, then guide you through the analysis. If you request a presentation, the Agent will generate it through the bundled presentation Skill rather than the CLI runner.

**Other AI agents:**

Start with this prompt:

```
Read AGENT_INSTRUCTIONS.md and follow the Business Analysis Learning Agent Skill.
I will provide a dataset.
```

## Output Directory

`--output-dir` is **required**. The CLI creates a timestamped subdirectory inside your chosen path to prevent silent overwrites:

```
<your-output-dir>/<dataset_name>_<timestamp>/
├── *_analysis.xlsx
├── *_report.html
├── *_report.pdf
└── *_audit_log.json
```

For example: `--output-dir ~/Desktop/my_analysis` creates `~/Desktop/my_analysis/sample_retail_sales_2026-06-03_143052/`.

## Troubleshooting

| Problem | Likely Fix |
|---------|-----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| `FileNotFoundError` | Check that `--input` path exists |
| Excel opens with warnings | This is a data analysis output, not a formatted template — ignoring warnings is safe |
| Multi-table analysis skips joins | The tool is conservative about join safety — check console output for details |

## What's Next

- Read `README.md` for a full project overview
- Read `templates/` for reusable analysis prompt templates
- Read `test_cases/` for sample datasets you can test with
