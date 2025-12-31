---
id: 002
title: Create Full-Stack Development Skill
stage: misc
date: 2025-12-30
surface: agent
model: claude-opus-4-5-20251101
feature: 001-fullstack-todo-app
branch: 001-fullstack-todo-app
user: operator
command: manual
labels: ["skill", "full-stack", "nextjs", "fastapi", "documentation"]
links:
  spec: specs/001-fullstack-todo-app/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/fullstack-nextjs-fastapi.md
tests:
  - null
---

## Prompt

Create a skill in skills directory. Details provided for Full-Stack Next.js + FastAPI Development skill covering:
- Technology Stack: Next.js 16+ (App Router), TypeScript, Tailwind CSS, FastAPI, SQLModel ORM, PostgreSQL (Neon), Better Auth with JWT
- Monorepo Structure: frontend/, backend/, specs/ directories
- Development Workflow: Read specs first, implement backend first, then frontend
- Code examples for: SQLModel models, FastAPI routes with auth, TypeScript API client, React components
- Key patterns for App Router, API communication, database operations, styling
- Security checklist for JWT verification, user isolation, secrets management
- Common tasks for adding features and testing integration

## Response snapshot

Created skill file at `.claude/skills/fullstack-nextjs-fastapi.md` containing:
- Complete technology stack reference
- Monorepo structure documentation
- Step-by-step development workflow
- Code examples for backend (SQLModel, FastAPI) and frontend (API client, React components)
- Key patterns for Next.js App Router, API communication, database operations
- Security checklist with JWT and user isolation requirements
- Common tasks guide for feature development and testing

## Outcome

- Impact: Established reusable skill documentation for full-stack development patterns
- Tests: N/A (documentation)
- Files: .claude/skills/fullstack-nextjs-fastapi.md created
- Next prompts: Use this skill as reference during /sp.implement phase
- Reflection: Skill provides comprehensive reference for the fullstack-todo-implementer agent

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual review PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
