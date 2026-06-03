# Sample Outputs

Representative outputs from the Business Analysis Learning Agent Skill. These demonstrate the quality and style of generated deliverables.

## Directory Overview

| Directory | What It Contains | Best For |
|-----------|-----------------|----------|
| `final_demo/` | Polished demo outputs (recommended showcase) | GitHub portfolio, first impression |
| `demo_interactive/` | Interactive agent workflow demo output | Seeing agent-driven workflow results |

## final_demo/ (Recommended Showcase)

### Retail Sales Demo (`final_demo/retail_demo/`)

A 12-record retail sales dataset analyzed with `audit_report` mode:

| File | Description |
|------|-------------|
| `sample_retail_sales_analysis.xlsx` | Excel workbook: data tables, ranking analysis, trend analysis, KPI dashboard |
| `sample_retail_sales_report.pdf` | PDF report: business interpretation, metric glossary, thinking models, recommendations |
| `sample_retail_sales_audit_log.json` | JSON audit log: full record of executed/skipped/recommended analysis methods |

### SaaS Churn Demo (`final_demo/` root)

A multi-table SaaS subscription dataset (merged from separate CSVs):

| File | Description |
|------|-------------|
| `saas_subscription_churn_merged_analysis.xlsx` | Excel workbook with multi-table join analysis |
| `saas_subscription_churn_merged_report.pdf` | PDF report with churn metrics and thinking models |

### Multi-Table Store Demo (`final_demo/multi_table_demo/`)

A multi-table store performance analysis (sales.csv + stores.csv, auto-joined on store_id):

| File | Description |
|------|-------------|
| `balearn_multi_Wbd5_merged_analysis.xlsx` | Excel workbook: relationship tables, ranking by region/size, distribution analysis |
| `balearn_multi_Wbd5_merged_report.pdf` | PDF report: thinking models, learning guide, field semantics, recommendations |
| `balearn_multi_Wbd5_merged_audit_log.json` | JSON audit log: executed/skipped methods and metrics |
| `multi_store_deck.html` | Standalone HTML presentation deck (Guizang A editorial style, 8 slides) |

### demo_interactive/

Output from the interactive agent workflow (retail + HTML presentation deck):

| File | Description |
|------|-------------|
| `retail_analysis.xlsx` | Excel analysis workbook |
| `retail_report.pdf` | PDF business report |
| `retail_deck.html` | Standalone HTML presentation deck (interactive, WebGL backgrounds) |

## Regenerating

To regenerate sample outputs:

```bash
# Retail demo
python3 scripts/run_analysis.py \
  --input test_cases/sample_retail_sales.csv \
  --mode audit_report \
  --output-dir sample_outputs/final_demo/retail_demo

# Smoke test
python3 scripts/run_analysis.py \
  --input test_cases/sample_retail_sales.csv \
  --mode beginner_summary \
  --output-dir output/smoke_test
```

Historical outputs from earlier iterations are archived at `docs/archive/generated_outputs/`.
