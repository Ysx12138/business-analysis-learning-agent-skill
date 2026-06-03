# Output Modes Template

Use this file to select output length and detail level.

## Mode: beginner_summary

Best for first-time users and business beginners.

Default toggles:

| Toggle | Status |
|---|---|
| dataset_risk_check | on, short |
| cleaning_impact | on, short |
| field_mapping | on, short |
| metric_formulas | on, core metrics only |
| recommendation_table | off |
| audit_detail | off |
| next_analysis | on, one item |

Output structure:

## 1. What This Dataset Is About

## 2. Top 3 Findings

| Finding | Business Meaning | Beginner Note |
|---|---|---|

## 3. Key Metrics You Should Understand

| Metric | Simple Meaning | Formula | Current Result |
|---|---|---|---|

## 4. One Thing to Be Careful About

## 5. What You Learned

## 5.1 Thinking Model (Pick 1)

Pick one thinking model and explain it in 3 to 5 lines:

- Decomposition (structure breakdown)
- Segment behavior divergence (layered differences)
- Proxy inference (indirect inference)
- Constraint vs preference (constraint as explanation)
- Leverage point identification

## 6. Recommended Next Step

## Mode: standard_report

Best for normal analysis delivery with learning value.

Default toggles:

| Toggle | Status |
|---|---|
| dataset_risk_check | on |
| cleaning_impact | on |
| field_mapping | on |
| metric_formulas | on |
| recommendation_table | on |
| audit_detail | off |
| next_analysis | on |

Output structure:

Use `templates/final_report_template.md`, but keep each section concise.

## Mode: medium (alias for standard_report)

Same as `standard_report`. Added for compatibility with `/balearn` command.
Output should include a basic Excel pivot table (1-2 sheets) with key findings.

## Mode: audit_report (alias: advanced)

Best for testing, portfolio documentation, detailed review, and portfolio-ready deliverables.

Default toggles:

| Toggle | Status |
|---|---|
| dataset_risk_check | on, full |
| cleaning_impact | on, full |
| field_mapping | on, full |
| metric_formulas | on, full |
| recommendation_table | on, full |
| audit_detail | on |
| next_analysis | on, full |

Output structure:

Use the full structure in `templates/final_report_template.md` and include complete reasoning tables.

### Required Deliverables (audit_report / advanced)

1. **Excel Pivot Table File** (`*_analysis.xlsx`)
   - One sheet per analysis dimension (overview, by contract, by tenure, by service, cross-analysis)
   - Dashboard sheet with KPI boxes and thinking model summary
   - Charts (bar/pie) placed next to source data
   - Headline KPI row at top (churn rate, key segment rates, revenue)

2. **PDF Thinking Model Report** (`*_thinking_models.pdf`)
   - Cover page with dataset summary
   - Executive summary with key metrics
   - All 5 thinking models with data evidence, business insight, and beginner takeaway
   - Self-check questions (all 5)
   - Action recommendations

## Toggle Syntax

The user can override a mode:

```text
Use beginner_summary, +metric_formulas, -audit_detail.
Use standard_report, -recommendation_table.
Use audit_report, +cleaning_impact.
```
