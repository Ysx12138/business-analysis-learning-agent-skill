# Decision Log

Architectural and workflow decisions for the Business Analysis Learning Agent Skill.

---

## 2026-05-31: Add PPT Generation to Workflow

### Context

After completing data analysis and generating Excel + PDF deliverables, users often need a presentation for reporting or sharing. Previously, PPT generation was not part of the standard workflow — it had to be requested and handled ad-hoc.

The bundled **guizang-ppt-skill** was tested and validated. It offers two
visual styles: 电子杂志风 and 瑞士国际主义风.

### Decision

Add an optional Step 9 (PPT Generation) at the end of the standard workflow (Section 5 in SKILL.md).

The step:
- Asks the user whether they want a PPT
- Offers two style options with brief descriptions
- Provides implementation instructions for the agent to invoke the correct skill

### Rationale

- PPT generation is a natural continuation of the analysis workflow
- Two validated styles give the user genuine choice
- Making it optional (step asks first) avoids disrupting the existing flow
- Agent now has clear instructions on which skill to read and how to apply it

### Files Changed

- `.claude/skills/business-analysis/SKILL.md` — added Step 9 in Section 5

### Alternatives Considered

- **Always generate PPT**: Rejected — not every analysis task needs a presentation
- **One fixed style**: Rejected — different audiences need different visual languages
- **Keep as separate manual step**: Rejected — users benefit from a guided flow

---

## 2026-05-31: Bundle PPT Templates into Business-Analysis Skill

### Context

Step 9 initially referenced an external skill path
(`.agents/skills/guizang-ppt-skill/`). These files only exist because that
skill was installed locally. A user who installs only the business-analysis
skill would get broken references.

### Decision

Bundle the essential template files and design references from all three PPT styles directly into the business-analysis skill's `assets/ppt/` directory (historical note; current presentation assets live under `vendor/agent_presentation_skills/`):

```
assets/ppt/
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

Updated SKILL.md Step 9 to reference these local paths.

### Rationale

- **Zero external dependency**: install business-analysis skill, get both PPT styles
- **Guaranteed availability**: template files are checked into the project, not loaded from remote skills
- **Clean separation**: styles live in their own subdirectories under `assets/ppt/`
- **Reasonable size**: ~440KB total, dominated by template HTML files

### Files Changed

- `.claude/skills/business-analysis/SKILL.md` — updated Step 9 implementation instructions to use local `assets/ppt/` paths
- `.claude/skills/business-analysis/assets/ppt/` — 12 new files (templates, themes, layouts, checklist, design references)

### Alternatives Considered

- **Keep referencing external skill paths**: Rejected — fragile, only works if user has installed all three skills
- **Create abstracted mini-templates instead of full copies**: Rejected — the inline-HTML templates are already self-contained; abstracting would risk incompatibility
- **Only bundle one style**: Rejected — defeats the purpose of giving users a choice

---

## 2026-06-01: Replace fpdf2 with reportlab for PDF Generation

### Context

The 5-dataset robustness test revealed 3 out of 6 discovered bugs were related to fpdf2:
1. **Unicode encoding errors** — em-dash and other Latin-1-exclusive characters crash generation
2. **x-position layout bugs** — `cell(0, ...)` followed by `multi_cell(0, ...)` requires manual `set_x(l_margin)` reset
3. **Table formatting limitations** — complex layouts are difficult to achieve

The project had an existing reportlab implementation (`scripts/generate_pdf_reportlab.py`) that was working correctly for Chinese-language PDFs.

### Decision

Replace all fpdf2-based PDF generation scripts with reportlab (v4.5.1), following the Anthropic official PDF Skill (`~/.claude-terminal/plugins/marketplaces/anthropic-agent-skills/skills/pdf/`).

Migration pattern: fpdf2's procedural `add_page()` → `cell()` → `ln()` approach was replaced with reportlab's declarative `SimpleDocTemplate` + `story` flowables (Paragraph, Spacer, Table, PageBreak, HRFlowable).

### Rationale

- reportlab is the Anthropic PDF Skill's recommended tool for creating PDFs
- Unicode support is native (no encoding workarounds needed)
- `SimpleDocTemplate` auto-manages page layout, margins, and flow
- `Table` + `TableStyle` provides clean, styled table output
- Page numbers via `onLaterPages` callback — no manual footer positioning
- Existing project code already had a working reportlab example

### Files Changed

| File | Change |
|------|--------|
| `scripts/generate_marketing_pdf.py` | fpdf2 → reportlab |
| `scripts/generate_saas_pdf.py` | fpdf2 → reportlab |
| `scripts/generate_retail_pdf.py` | fpdf2 → reportlab |
| `scripts/generate_reviews_pdf.py` | New file (reportlab, previously no PDF) |
| `scripts/generate_financial_pdf.py` | fpdf2 → reportlab |
| `docs/changelog.md` | Added v0.5.0 entry |
| `portfolio/development_logs/开发日志/开发日志0.5.md` | Added migration section |

### Alternatives Considered

- **Keep fpdf2 with workarounds**: Rejected — 3 distinct bugs found across multiple datasets, each requiring fragile workarounds
- **WeasyPrint HTML→PDF conversion**: Rejected — requires system-level GTK/Pango libraries unavailable on macOS
- **pypdf/pdfplumber (read-oriented)**: Rejected — these are PDF reading libraries, not creation libraries
