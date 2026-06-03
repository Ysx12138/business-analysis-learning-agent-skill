# MVP Run Guide

This guide helps you run the skill with the smallest possible workflow.

## 1. Prerequisites

- You have an AI Agent environment (for example, Codex or Claude Code).
- You can provide a dataset file (CSV or Excel).
- This repository is available in the same workspace as your Agent.

## 2. Minimal Run Flow

1. Open this project folder in your Agent workspace.
2. Provide a dataset file.
3. Use one prompt from `prompts/`.
4. Choose an output mode: `beginner_summary`, `standard_report`, or `audit_report`.
5. Compare output with `evaluation_checklist.md`.

If no mode is specified, the Agent should use `beginner_summary`.

## 3. Output Modes

| Mode | Best For | Detail Level |
|---|---|---|
| `beginner_summary` | first-time users and business beginners | short |
| `standard_report` | normal analysis delivery | medium |
| `audit_report` | testing, portfolio logs, and detailed review | full |

You can also turn modules on or off:

```text
Use beginner_summary, +metric_formulas, -audit_detail.
Use standard_report, -recommendation_table.
Use audit_report, +dataset_risk_check, +cleaning_impact.
```

## 3. Recommended Prompt Files

- `prompts/retail_sales_prompt.md`
- `prompts/customer_segmentation_prompt.md`
- `prompts/product_performance_prompt.md`

## 4. Expected Output Structure

For `beginner_summary`, the output should contain:

1. What This Dataset Is About
2. Top 3 Findings
3. Key Metrics You Should Understand
4. One Thing to Be Careful About
5. What You Learned
6. Recommended Next Step

For `standard_report` and `audit_report`, the output should follow the sections defined in `SKILL.md`:

1. Task Understanding
2. Dataset Overview
3. Dataset Risk Check
4. Cleaning Impact Assessment
5. Field to Business Question Mapping
6. Business Questions and Methods
7. Key Metrics and Calculations
8. Key Findings
9. Business Interpretation
10. Recommendations
11. Metrics and Concepts Explained
12. Beginner Learning Notes
13. Limitations
14. Recommended Next Analysis

## 5. Pass Criteria (MVP)

The run is considered successful when the Agent:

- explains business meaning of key fields
- explains why analysis methods are selected
- explains cleaning rules and their impact
- shows formulas and current calculations for core metrics
- explains metrics and abbreviations clearly
- distinguishes facts, interpretation, and assumptions
- gives actionable recommendations tied to evidence
- provides beginner learning notes

## 6. Quick Troubleshooting

If output is too technical:

- ask the Agent to simplify language for business beginners
- ask the Agent to explain abbreviations at first use

If output is only charts or code:

- ask the Agent to follow `SKILL.md` sections explicitly
- require business interpretation and learning notes before final answer
