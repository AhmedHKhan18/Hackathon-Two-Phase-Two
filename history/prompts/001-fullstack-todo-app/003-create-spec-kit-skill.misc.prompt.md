---
id: 003
title: Create Spec-Kit Plus Workflow Skill
stage: misc
date: 2025-12-30
surface: agent
model: claude-opus-4-5-20251101
feature: 001-fullstack-todo-app
branch: 001-fullstack-todo-app
user: operator
command: manual
labels: ["skill", "spec-kit", "workflow", "documentation", "spec-driven"]
links:
  spec: specs/001-fullstack-todo-app/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/spec-kit-plus-workflow.md
tests:
  - null
---

## Prompt

Create another skill for Spec-Kit Plus Development Workflow covering:
- Spec organization structure (features/, api/, database/, ui/)
- Configuration via .spec-kit/config.yaml
- Development workflow: read spec first, follow layered CLAUDE.md context, implement backend then frontend
- Spec file format templates (feature, API, database)
- Referencing specs in prompts and CLAUDE.md files
- Benefits of spec-first development
- Common workflows for adding/modifying features
- Best practices for spec writing, organization, and implementation
- Integration with Claude Code
- Troubleshooting guide

## Response snapshot

Created skill file at `.claude/skills/spec-kit-plus-workflow.md` containing:
- Complete spec organization structure documentation
- Configuration reference for .spec-kit/config.yaml
- Step-by-step development workflow (read spec → backend → frontend)
- Templates for feature, API, and database spec files
- Spec referencing syntax for prompts and CLAUDE.md
- Benefits table for spec-first approach
- Common workflows for feature development
- Best practices for writing and organizing specs
- Claude Code integration patterns
- Troubleshooting guide for common issues

## Outcome

- Impact: Established comprehensive Spec-Kit Plus workflow documentation as reusable skill
- Tests: N/A (documentation)
- Files: .claude/skills/spec-kit-plus-workflow.md created
- Next prompts: Reference this skill when using /sp.specify, /sp.plan, /sp.tasks commands
- Reflection: Skill provides complete reference for spec-driven development workflow

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual review PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
