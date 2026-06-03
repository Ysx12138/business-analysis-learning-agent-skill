# Agent Integration Guide

This guide explains how to use Business Analysis Learning Agent Skill in different AI agent environments.

The core instruction is platform-agnostic:

- `SKILL.md` defines the behavior.
- `AGENT_INSTRUCTIONS.md` provides a portable instruction wrapper.
- `.claude/` provides an optional Claude Code adapter.

## Universal Integration Pattern

Any agent should follow this pattern:

1. Load or read `SKILL.md`.
2. Accept a CSV or Excel dataset from the user.
3. Ask the user to choose an output mode before analysis.
4. Ask the user where to save output files (Excel, HTML, PDF, audit log). Never write to the Skill installation directory without confirmation.
5. Default all user-facing outputs to Chinese unless the user requests English.
6. Analyze the dataset and teach the business reasoning while doing the work.
7. Generate files when the environment supports file creation.

## Claude Code

Open the repository root in Claude Code and run:

```text
/balearn
```

The Claude Code adapter is stored in:

```text
.claude/commands/balearn.md
.claude/skills/business-analysis/SKILL.md
```

## Codex

Open the repository root in Codex and use:

```text
Read SKILL.md and AGENT_INSTRUCTIONS.md. Then run the Business Analysis Learning Agent Skill on my dataset.
```

Codex should use `SKILL.md` as the behavioral spec and create deliverable files when file tools are available.

## Cursor

Open the repository in Cursor and attach or reference the dataset file. Use:

```text
Use SKILL.md as the project instruction. Before analysis, ask me to choose beginner_summary, standard_report, or audit_report.
```

If Cursor is configured with project rules, paste the content of `AGENT_INSTRUCTIONS.md` into a project rule and point it to `SKILL.md`.

## ChatGPT, Claude, Gemini, or Other Web Agents

If the agent supports file upload:

1. Upload the dataset.
2. Upload or paste `AGENT_INSTRUCTIONS.md`.
3. Upload or paste `SKILL.md` if the agent cannot access the repository.
4. Ask the agent to follow the skill and choose an output mode before starting.

If the agent cannot create Excel, PDF, or PPT files, ask it to provide:

- pivot-ready tables
- chart specifications
- report content
- slide outline

These can then be copied into spreadsheet or presentation tools.

## Minimum Agent Requirements

For text-only use:

- can read instructions
- can inspect a dataset schema or sample rows
- can produce structured analysis output

For full deliverables:

- can read CSV or Excel files
- can create or modify spreadsheet files
- can generate PDF or document files
- can generate HTML/PPT deliverables for presentations

Presentation deliverables must be created through the Agent workflow after reading the selected
bundled presentation Skill under `vendor/agent_presentation_skills/`. The universal runner does
not generate presentations.

## Compatibility Boundary

This project does not assume one specific agent runtime.

Claude Code commands are only an adapter. The reusable skill is the instruction system defined by `SKILL.md`, templates, examples, and test cases.
