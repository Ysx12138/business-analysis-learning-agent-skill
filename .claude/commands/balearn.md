---
name: balearn
description: Run the Business Analysis Learning Skill (ask for mode first; default Chinese outputs)
---

When the user invokes `/balearn`, do the following:

1) Confirm inputs
- Dataset file (CSV/Excel) or a schema description.
- Business context (domain, goal/decision to support, timeframe).

2) Ask for output mode BEFORE analysis (required)
Ask the user to choose one:
- `beginner_summary` (default; short, beginner-friendly)
- `standard_report` (medium depth)
- `audit_report` (full detail for review/testing)

Do not proceed until the user selects a mode (or explicitly chooses the default).

3) Ask for output folder BEFORE analysis (required)
Ask where to save Excel, HTML, PDF, PPT, and audit log files.
If the user doesn't know, recommend:
  `<数据文件所在目录>/analysis_outputs/<数据集名称_日期时间>/`
Never write output files into the Skill installation directory without asking.

4) Language default
- Default output language is **Chinese** for all deliverables: text report, Excel, PDF, PPT.
- If the user requests English, switch to English (or bilingual if asked).

5) Execute the workflow
Follow the spec in:
- `.claude/skills/business-analysis/SKILL.md`

If the user requests a presentation, generate it only after reading the selected bundled
presentation Skill under `vendor/agent_presentation_skills/`. Do not use a CLI PPT shortcut
or a generic Python PPTX renderer.
