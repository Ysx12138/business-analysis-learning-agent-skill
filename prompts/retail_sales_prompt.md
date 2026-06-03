# Retail Sales Prompt

Analyze this retail sales dataset using the Business Analysis Learning Agent Skill.

Default output mode:

- Use `beginner_summary` unless the user asks for `standard_report` or `audit_report`.

Requirements:

- Follow the workflow and output structure in `SKILL.md`.
- Explain field business meaning (for example: order_date, product_category, sales_amount, customer_id, store_id).
- Include a Dataset Risk Check before conclusions.
- Include a Cleaning Impact Assessment with business reason, rows removed, percentage removed, affected analysis, and treatment.
- Include a Field -> Metric -> Business Question -> Analysis Method table.
- Explain why each analysis method is selected.
- Explain core metrics with formula, current calculation, business meaning, beginner note, and limitation.
- Explain metrics and abbreviations in plain language (for example: revenue, order count, AOV, contribution rate).
- Separate data facts, interpretations, and assumptions.
- Format recommendations as Finding -> Business Meaning -> Recommended Action -> Metric to Track -> Data Needed.
- End with beginner learning notes and a structured Recommended Next Analysis section.

Use the final structure defined in `templates/final_report_template.md`.
