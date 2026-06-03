# Legacy Scripts

These scripts were created during earlier validation iterations (v0.1–v0.5) to test individual datasets and generate outputs manually. They are kept for historical reference only.

**Do not use these for new analyses.** Use `scripts/run_analysis.py` instead.

These scripts are **not part of the main `run_analysis.py` pipeline**. They operate independently and predate the universal runner architecture.

**Note:** These scripts contain hardcoded absolute file paths from the original developer's machine. They will not run without path modifications. They are preserved as design references, not as executable tools.

## Dataset-Specific Analysis Scripts

- `marketing_campaign_analysis.py` — Marketing campaign dataset (v0.4)
- `saas_churn_analysis.py` — SaaS churn dataset (v0.4)
- `retail_analysis.py` — Retail operations dataset (v0.4)
- `reviews_analysis.py` — Product reviews dataset (v0.4)
- `financial_analysis.py` — Financial analysis dataset (v0.4)
- `online_retail_analysis.py` — Online retail dataset (v0.1/v0.2)

## Dataset-Specific Generation Scripts

These generate Excel and PDF outputs for specific datasets. They predate the universal renderers (`scripts/renderers/`):

- `generate_excel.py`, `generate_excel_standard.py`
- `generate_financial_excel.py`, `generate_financial_pdf.py`
- `generate_marketing_excel.py`, `generate_marketing_pdf.py`
- `generate_online_retail_excel.py`
- `generate_pdf_reportlab.py`
- `generate_retail_excel.py`, `generate_retail_pdf.py`
- `generate_reviews_pdf.py`
- `generate_saas_excel.py`, `generate_saas_pdf.py`
