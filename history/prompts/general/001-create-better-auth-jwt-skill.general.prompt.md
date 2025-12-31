---
id: 001
title: Create Better Auth JWT Skill
stage: general
date: 2025-12-30
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: 001-fullstack-todo-app
user: user
command: create skill
labels: ["skill", "authentication", "jwt", "better-auth"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/better-auth-jwt.md
tests:
  - null
---

## Prompt

create a skill in this project. here is the details for the skills: ---
name: better-auth-jwt
description: Implement authentication using Better Auth with JWT tokens across Next.js frontend and FastAPI backend. Use when implementing user signup/signin, protecting API routes, verifying authenticated users, or integrating JWT token flow between separate frontend and backend services.
---

# Better Auth + JWT Authentication

[Full skill content provided with architecture diagram, implementation steps for frontend Better Auth setup, auth pages, API client with JWT, backend JWT verification, protected routes, security checklist, common issues, testing guidance, benefits, and best practices]

## Response snapshot

Created skill file at `.claude/skills/better-auth-jwt.md` containing comprehensive documentation for implementing Better Auth with JWT tokens across Next.js frontend and FastAPI backend. The skill covers:

1. Architecture overview with JWT flow diagram
2. Frontend: Better Auth setup, auth provider, sign-up/sign-in pages
3. Frontend: API client with JWT token handling and automatic 401 redirect
4. Backend: JWT verification using python-jose, protected route patterns
5. Security checklist for endpoints and environment variables
6. Common issues and troubleshooting
7. Testing authentication including user isolation tests
8. Best practices for production deployment

## Outcome

- Impact: Added reusable skill documentation for authentication implementation
- Tests: N/A - documentation only
- Files: 1 file created (.claude/skills/better-auth-jwt.md)
- Next prompts: Implement authentication using this skill
- Reflection: Straightforward skill creation following existing skill format

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
