# Product Performance Prompt

Analyze this product performance dataset using the Business Analysis Learning Agent Skill.

Default output mode:

- Use `beginner_summary` unless the user asks for `standard_report` or `audit_report`.

Requirements:

- Follow the workflow in `SKILL.md`.
- Explain product-level and category-level business questions.
- Include a Dataset Risk Check before conclusions.
- Include a Cleaning Impact Assessment when records are removed or separated.
- Include a Field -> Metric -> Business Question -> Analysis Method table.
- Analyze revenue, quantity, cost, profit, and margin relationship.
- Explain why high sales does not always imply high profit.
- Explain core metrics with formula, current calculation, business meaning, beginner note, and limitation.
- Explain metrics and abbreviations in plain language.
- Separate data facts, interpretation, and assumptions.
- Format recommendations as Finding -> Business Meaning -> Recommended Action -> Metric to Track -> Data Needed.
- End with beginner learning notes and a structured Recommended Next Analysis section.

Use `templates/business_explanation_template.md` and `templates/final_report_template.md`.
