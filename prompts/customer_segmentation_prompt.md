# Customer Segmentation Prompt

Analyze this customer dataset using the Business Analysis Learning Agent Skill.

Default output mode:

- Use `beginner_summary` unless the user asks for `standard_report` or `audit_report`.

Requirements:

- Follow `SKILL.md` workflow.
- Translate fields into business questions.
- Include a Dataset Risk Check before conclusions.
- Include a Field -> Metric -> Business Question -> Analysis Method table.
- Focus on segmentation logic using purchase frequency, total spending, recency, and repeat purchase behavior.
- Explain each segmentation metric with formula, current calculation, business meaning, beginner note, and limitation.
- Explain each segment in beginner-friendly language.
- Explain relevant metrics and terms when first used.
- Separate evidence from assumptions.
- Provide practical recommendations using Finding -> Business Meaning -> Recommended Action -> Metric to Track -> Data Needed.
- End with beginner learning notes and a structured Recommended Next Analysis section.

Use `templates/analysis_workflow_template.md` and `templates/final_report_template.md`.
