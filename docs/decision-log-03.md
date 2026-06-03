# Decision 03: Bundle PPT Generation into Business-Analysis Skill

**Date:** 2026-05-31

## Context

After completing data analysis, users often need a presentation. Two PPT generation styles were tested and validated:

- 电子杂志风 (guizang-ppt-skill Style A)
- 瑞士国际主义风 (guizang-ppt-skill Style B)

Initially, Step 9 in SKILL.md referenced an external skill path
(`.agents/skills/guizang-ppt-skill/`). These files only exist because that
skill was installed locally. A user who installs only the business-analysis
skill would get broken references.

## Decision

Bundle the essential template files and design references from all three PPT styles directly into the business-analysis skill.

### Files Added

```
.claude/skills/business-analysis/assets/ppt/ (historical note; current presentation assets live under `vendor/agent_presentation_skills/`)
├── guizang-style-a/
│   ├── template.html         # 电子杂志风 full template
│   ├── themes.md             # 5 theme references
│   ├── layouts.md            # slide layout catalog
│   └── motion.min.js         # WebGL / transition support
├── guizang-style-b/
│   ├── template-swiss.html   # 瑞士国际主义风 full template
│   ├── themes-swiss.md       # 4 accent color references
│   ├── layouts-swiss.md      # 22 S layout catalog
│   └── motion.min.js         # WebGL / transition support
├── guizang-checklist.md      # QA checklist for both styles
```

### Files Changed

- `.claude/skills/business-analysis/SKILL.md` — Step 9 updated to reference `assets/ppt/` local paths instead of external skill paths

### Rationale

- **Zero external dependency**: install business-analysis skill, get both PPT styles
- **Guaranteed availability**: template files are in-repo, not loaded from remote skills
- **Clean separation**: each style in its own subdirectory under `assets/ppt/`
- **Reasonable size**: ~440KB, dominated by inline HTML templates

## Alternatives Considered

- **Keep referencing external paths**: rejected — fragile, only works if user has installed all three skills separately
- **Create mini-templates instead of full copies**: rejected — the HTML templates are already self-contained; abstraction risks incompatibility
- **Only bundle one style**: rejected — defeats the purpose of giving users a choice

---

## Fix: Deliverable Gap (v0.3)

**Date:** 2026-05-31

### Problem

Excel + PDF deliverables were only required in `audit_report` (advanced) mode. When running analysis in `beginner_summary` (default) or `standard_report` mode, the skill definition did not require file deliverables — only text output. This caused the actual analysis run (online_retail dataset) to skip Excel and PDF generation.

### Root Cause

The "Required Deliverables" section was nested under **Mode C: audit_report / advanced** only, not as a general requirement.

### Fix

Moved "Required Deliverables (Excel + PDF)" from Mode C subsection to a top-level section under Standard Workflow, applying to ALL output modes. Removed the duplicate subsection from Mode C.

### Files Changed

- `.claude/skills/business-analysis/SKILL.md` — Required Deliverables promoted from Mode C subsection to global section between Step 9 and Section 6
- `scripts/generate_online_retail_excel.py` — newly added for this dataset
- `scripts/generate_online_retail_pdf.py` — originally added for this dataset; later removed after PDF generation migrated from fpdf2 to reportlab
