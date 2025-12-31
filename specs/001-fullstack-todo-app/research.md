# Research: Full-Stack Todo Web Application

**Feature**: 001-fullstack-todo-app
**Date**: 2025-12-30
**Phase**: 0 - Research

## Overview

This document captures technology decisions, alternatives considered, and research findings for the Phase II Todo application implementation.

---

## 1. Authentication Strategy

### Decision: Better Auth with JWT Plugin

**Rationale**: Constitution mandates Better Auth for frontend authentication and JWT tokens for API security. Better Auth is a modern TypeScript authentication library designed specifically for Next.js applications.

**Alternatives Considered**:

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| Better Auth + JWT | Native Next.js support, built-in JWT plugin, active development | Newer library, less community examples | SELECTED (mandated) |
| NextAuth.js | Mature, large community, many providers | Heavier setup for simple email/password, session-based by default | Rejected - not mandated |
| Auth0 | Enterprise-ready, managed service | External dependency, cost at scale, overkill for Phase II | Rejected |
| Custom JWT | Full control | Security risk, reinventing wheel | Rejected |

**Key Integration Points**:
- Better Auth runs on frontend only (constitution rule)
- JWT issued with `sub` claim containing user ID
- Shared secret (BETTER_AUTH_SECRET) for signature verification
- 7-day token expiration (configurable)

---

## 2. Backend JWT Verification

### Decision: python-jose with HS256

**Rationale**: python-jose is the de facto standard for JWT handling in Python/FastAPI applications. HS256 (HMAC-SHA256) provides symmetric key verification using the shared secret.

**Alternatives Considered**:

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| python-jose | Well-maintained, FastAPI examples available | Requires cryptography dependency | SELECTED |
| PyJWT | Simpler, lighter | Less features | Acceptable alternative |
| authlib | Full OAuth support | Overkill for JWT-only verification | Rejected |
| Manual verification | None | Security risk | Rejected |

**Implementation Pattern**:
- HTTPBearer security scheme for token extraction
- Dependency injection for user context
- JWTError handling returns 401

---

## 3. Database Connection Strategy

### Decision: SQLModel with Neon PostgreSQL

**Rationale**: Constitution mandates SQLModel ORM and Neon PostgreSQL. SQLModel combines Pydantic models with SQLAlchemy, providing type safety and ORM capabilities.

**Alternatives Considered**:

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| SQLModel | Pydantic integration, type hints, FastAPI native | Newer than SQLAlchemy | SELECTED (mandated) |
| SQLAlchemy (raw) | Battle-tested, flexible | Verbose, no Pydantic integration | Rejected |
| Tortoise ORM | Async-first | Less FastAPI integration | Rejected |
| Prisma Python | Type-safe | Experimental, Node dependency | Rejected |

**Connection Handling**:
- Synchronous connections sufficient for Phase II
- Connection pooling via SQLModel/SQLAlchemy defaults
- Neon serverless handles scaling automatically

---

## 4. Frontend State Management

### Decision: React State + Better Auth Session

**Rationale**: For Phase II scope (task list per user), React's built-in useState and useEffect are sufficient. Better Auth handles session state. No additional state management library needed.

**Alternatives Considered**:

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| React useState/useEffect | Simple, no dependencies | May need upgrade for complex state | SELECTED |
| Zustand | Lightweight, simple API | Additional dependency | Reserved for Phase III |
| Redux Toolkit | Powerful, devtools | Overkill for todo list | Rejected |
| Jotai/Recoil | Atomic state | Learning curve | Rejected |

**Pattern**:
- Component-level state for UI interactions
- Fetch data on component mount
- Refetch after mutations

---

## 5. API Client Architecture

### Decision: Centralized fetch wrapper in lib/api.ts

**Rationale**: Constitution requires centralized API client. A single module handles all backend communication, JWT attachment, and error handling.

**Alternatives Considered**:

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| Custom fetch wrapper | Full control, no dependencies | Manual implementation | SELECTED |
| Axios | Interceptors, widespread | Additional dependency | Acceptable alternative |
| TanStack Query | Caching, refetching | Complexity for simple CRUD | Reserved for Phase III |
| tRPC | Type safety | Requires backend changes | Rejected |

**Implementation**:
- getAuthToken() extracts JWT from Better Auth session
- All requests include Authorization header
- 401 triggers redirect to /signin
- Type-safe request/response interfaces

---

## 6. Styling Approach

### Decision: Tailwind CSS

**Rationale**: Tailwind is the standard CSS framework for Next.js applications. Utility-first approach enables rapid UI development without context switching.

**Alternatives Considered**:

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| Tailwind CSS | Utility-first, Next.js native | Learning curve | SELECTED |
| CSS Modules | Scoped, no runtime | Verbose, manual theming | Acceptable alternative |
| styled-components | Component-based | Runtime cost, SSR complexity | Rejected |
| Chakra UI | Component library | Additional dependency | Rejected |

**Conventions**:
- Mobile-first responsive design
- Consistent spacing scale
- No custom CSS files for Phase II

---

## 7. Form Handling

### Decision: Controlled components with native validation

**Rationale**: For simple forms (sign-in, sign-up, task create/edit), React controlled components with HTML5 validation provide sufficient functionality without additional dependencies.

**Alternatives Considered**:

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| Controlled components | Simple, no dependencies | Manual validation | SELECTED |
| React Hook Form | Performance, validation | Dependency for simple forms | Reserved for Phase III |
| Formik | Full-featured | Heavy, older API | Rejected |
| Zod + React Hook Form | Type-safe validation | Multiple dependencies | Reserved for Phase III |

**Validation Strategy**:
- Required fields via HTML required attribute
- Max length via maxLength attribute
- Server-side validation as backup

---

## 8. Error Handling Strategy

### Decision: HTTP status codes + user-friendly messages

**Rationale**: Standard HTTP status codes for API errors, with frontend translation to user-friendly messages.

**Error Taxonomy**:

| Code | Meaning | Frontend Handling |
|------|---------|-------------------|
| 400 | Validation error | Show field-specific message |
| 401 | Unauthorized | Redirect to /signin |
| 403 | Forbidden | Show access denied message |
| 404 | Not found | Show not found message |
| 500 | Server error | Show generic error + retry |

**Backend Pattern**:
- HTTPException with detail message
- Pydantic validation errors auto-converted to 422
- Global exception handler for unexpected errors

---

## 9. Testing Strategy

### Decision: Manual validation for Phase II

**Rationale**: Constitution does not mandate automated tests for Phase II. Manual testing per acceptance scenario ensures feature completeness. Automated tests reserved for Phase III.

**Alternatives Considered**:

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| Manual validation | Fast to implement, sufficient for scope | Not automated | SELECTED |
| pytest + Jest | Automated, regression protection | Time investment | Reserved for Phase III |
| Playwright E2E | Full flow coverage | Complex setup | Reserved for Phase III |
| Cypress | Interactive debugging | Additional tooling | Rejected |

**Validation Approach**:
- Checklist per acceptance scenario
- Security-focused edge case testing
- User isolation verification

---

## 10. Deployment Considerations

### Decision: Local development focus

**Rationale**: Phase II focuses on functional implementation. Production deployment details are noted but not primary scope.

**Environment Strategy**:
- .env.local for frontend secrets
- .env for backend secrets
- Both in .gitignore
- Document required variables in CLAUDE.md files

**Production Notes** (for future reference):
- CORS configuration for production origin
- HTTPS enforcement
- Environment variable injection
- Separate database for production

---

## Summary of Decisions

| Area | Decision | Mandated by Constitution |
|------|----------|-------------------------|
| Frontend Auth | Better Auth | Yes |
| Token Format | JWT | Yes |
| Backend Framework | FastAPI | Yes |
| ORM | SQLModel | Yes |
| Database | Neon PostgreSQL | Yes |
| JWT Library | python-jose | No (best practice) |
| State Management | React useState | No (sufficient for scope) |
| Styling | Tailwind CSS | No (Next.js standard) |
| API Client | Custom fetch wrapper | Yes (centralized required) |
| Testing | Manual validation | No (Phase II scope) |

---

## Unresolved Items

None. All technical decisions are finalized and aligned with constitution requirements.

---

## References

- [Better Auth Documentation](https://www.better-auth.com/)
- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Neon PostgreSQL](https://neon.tech/docs)
- [python-jose](https://python-jose.readthedocs.io/)
