# Claude Code Handoff: v0.7 Alignment Tasks

This file is the working handoff for Claude Code.

## Current Project State

The project is no longer just a prompt-style skill. It has evolved into a platform-agnostic Agent Skill with a runnable universal analysis engine.

Current version state:

- v0.4: Claude Code skill entry, output modes, Excel/PDF deliverables, optional PPT step
- v0.5: real-world robustness testing across 5 business datasets
- v0.6 / v0.6.2: universal analysis engine, multi-table relationship detection, generic renderers
- v0.7: presentation workflow redesigned into interactive style selection + standalone HTML deck generation

Important logs to read before editing:

- `/Users/sx/Desktop/AI-Data-Analysis-Learning-Skill/portfolio/development_logs/开发日志/开发日志0.6.md`
- `/Users/sx/Desktop/AI-Data-Analysis-Learning-Skill/portfolio/development_logs/开发日志/开发日志0.7.md`
- `/Users/sx/Desktop/AI-Data-Analysis-Learning-Skill/portfolio/development_logs/决策记录/决策记录0.3.md`

## Key Architectural Direction

Do not position this as a Claude Code-only project.

The correct positioning is:

> A platform-agnostic Agent Skill for learning-oriented business data analysis, with optional adapters for Claude Code and other agent environments.

The core reusable behavior lives in:

- `SKILL.md`
- `AGENT_INSTRUCTIONS.md`
- `templates/`
- `test_cases/`
- `scripts/run_analysis.py`
- `scripts/core/`
- `scripts/renderers/`

Claude Code-specific files under `.claude/` are only adapters.

## Next Task: v0.7 Documentation and Entry Alignment

The next task is not to add new features. The next task is to align documentation, entry points, and user-facing instructions with the current v0.7 architecture.

### 1. Update README.md

Rewrite or update the relevant sections so README reflects the current project:

- Explain that this is a platform-agnostic Agent Skill.
- Explain that Claude Code is only one supported adapter.
- Add current architecture:
  - `scripts/run_analysis.py`
  - `scripts/core/`
  - `scripts/renderers/`
  - `.claude/`
- Add quick start for universal runner:

```bash
python scripts/run_analysis.py \
  --input "/path/to/dataset_or_folder" \
  --mode beginner_summary \
  --language zh \
  --output-dir output/demo_run
```

- Add current deliverables:
  - Excel workbook
  - PDF report
  - optional standalone HTML deck
- Explain v0.7 presentation flow:
  - finish Excel/PDF first
  - ask whether user wants a presentation
  - if yes, choose Guizang A / Guizang B
  - generate standalone HTML deck

### 2. Update SKILL.md

Ensure `SKILL.md` matches v0.7:

- Keep repository artifacts in English.
- Default user-facing outputs to Chinese.
- Keep Step 0: ask output mode before analysis.
- Keep Step 9, but make sure it says presentation generation is interactive and HTML-first.
- Avoid presenting PPTX as the default format.
- Mention CLI `--ppt` only as an optional shortcut, not the main workflow.
- Keep Claude Code references minimal; do not make the core skill Claude-specific.

### 3. Update docs/universal_runner_design.md

This file currently reads like a future design document.

Update it to distinguish:

- implemented in v0.6 / v0.6.2
- still planned

Implemented items should include:

- `scripts/run_analysis.py`
- data intake
- field semantics
- metric registry
- analysis planner
- result schema
- relationship detector
- Excel renderer
- PDF renderer
- PPT renderer / presentation renderer

Planned or partial items should be clearly labeled.

### 4. Add QUICKSTART.md or INSTALL.md

Create a concise beginner-friendly quick start.

It should cover:

- how to run with a single CSV
- how to run with a folder of multiple CSVs
- how to choose mode
- how language works (`zh` default, English if requested)
- where outputs are saved
- how Claude Code users can invoke `/balearn`
- how non-Claude agents can use `AGENT_INSTRUCTIONS.md`

Keep it practical. Avoid long theory.

### 5. Clarify scripts/ Directory

Do not delete more scripts unless clearly obsolete.

Add a small `scripts/README.md` explaining:

- recommended entry: `run_analysis.py`
- `scripts/core/` contains reusable analysis modules
- `scripts/renderers/` contains reusable output renderers
- dataset-specific scripts are validation/demo scripts from earlier iterations

This reduces confusion without breaking historical validation files.

## Do Not Do

- Do not add a web UI yet.
- Do not rewrite the universal runner unless documentation review reveals a clear bug.
- Do not make the project Claude Code-only.
- Do not remove validation scripts unless they are confirmed obsolete.
- Do not introduce a new framework.
- Do not change default user-facing output language from Chinese.

## Acceptance Criteria

The v0.7 alignment is done when:

- README explains the current v0.7 architecture clearly.
- A new user can find the recommended runner command within 30 seconds.
- `SKILL.md` matches the interactive HTML presentation workflow.
- `docs/universal_runner_design.md` no longer reads as purely future tense.
- `QUICKSTART.md` or `INSTALL.md` exists.
- `scripts/README.md` clarifies recommended vs legacy/demo scripts.
- Claude Code `/balearn` remains available but is not positioned as the only way to use the skill.

## Suggested Final Check

After editing, run:

```bash
rg -n "Claude Code-only|PPTX default|future design|fpdf|FPDF" .
```

Then inspect any hits and remove or clarify outdated wording.
