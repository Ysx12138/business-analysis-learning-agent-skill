# Changelog

## v0.5.0

Migrated PDF generation from fpdf2 to reportlab (Anthropic official PDF Skill recommendation).

- Replaced all fpdf2-based PDF scripts with reportlab `SimpleDocTemplate`
- Added PDF report for reviews dataset (was missing)
- Fixed fpdf2 issues: Unicode encoding errors, x-position layout bugs, table formatting limitations
- Updated development log with migration details

---

Strengthened the skill from a basic analysis report workflow into a more explicit learning-oriented analysis workflow.

Added:

- Output mode control: `beginner_summary`, `standard_report`, and `audit_report`
- User-controlled module toggles for risk checks, cleaning impact, formulas, recommendations, and audit detail
- `templates/output_modes_template.md`
- Thinking models teaching toolkit (5 reusable models) and `templates/thinking_models_template.md`
- Learning-oriented reasoning requirements for every major analysis step
- Dataset Risk Check module
- Cleaning Impact Assessment module
- Field -> Metric -> Business Question -> Analysis Method mapping
- Required metric formula and current calculation format
- Recommendation format: Finding -> Business Meaning -> Recommended Action -> Metric to Track -> Data Needed
- Structured Recommended Next Analysis section
- Updated final report template
- Updated evaluation checklist
- Updated prompt files for retail, customer, and product analysis

## v0.1.0

Initial version.

Added:

- Core SKILL.md
- Business analysis learning workflow
- Beginner-friendly explanation rules
- Business reasoning rules
- Metric glossary template
- Final report template
- Retail sales test case
- Customer analysis test case
- Product performance test case
- Basic usage guide
- Design principles
