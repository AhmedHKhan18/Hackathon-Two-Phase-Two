# Implementation Plan: Full-Stack Todo Web Application

**Branch**: `001-fullstack-todo-app` | **Date**: 2025-12-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-fullstack-todo-app/spec.md`

## Summary

Transform an existing Phase I in-memory console Todo app into a production-ready full-stack web application with multi-user support, persistent storage, and JWT-secured API. The frontend uses Next.js with Better Auth for authentication, while the backend uses FastAPI with SQLModel for data persistence to Neon PostgreSQL. JWT tokens issued by Better Auth are verified by the backend to enforce user-scoped data isolation.

## Technical Context

**Language/Version**:
- Frontend: TypeScript (Next.js 16+ with App Router)
- Backend: Python 3.11+ (FastAPI)

**Primary Dependencies**:
- Frontend: Next.js, Better Auth, @better-auth/react, Tailwind CSS
- Backend: FastAPI, SQLModel, python-jose[cryptography], uvicorn

**Storage**: Neon Serverless PostgreSQL

**Testing**:
- Manual validation per acceptance scenario
- Backend: pytest (optional for Phase II)
- Frontend: Jest/Vitest (optional for Phase II)

**Target Platform**: Web browsers (Chrome, Firefox, Safari, Edge - latest 2 versions)

**Project Type**: Web application (monorepo with frontend + backend)

**Performance Goals**:
- Task list displays within 2 seconds for up to 100 tasks
- Account registration and sign-in under 60 seconds
- Task creation under 10 seconds from dashboard load

**Constraints**:
- 50 concurrent authenticated users without degradation
- Responsive UI from 320px to 1920px screen width
- Title limit: 200 characters
- Description limit: 2000 characters

**Scale/Scope**:
- Multi-user system with complete user isolation
- Up to 100 tasks per user (Phase II performance target)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Spec-Driven Only

| Check | Status | Notes |
|-------|--------|-------|
| Spec exists before implementation | PASS | spec.md complete and validated |
| Spec is single source of truth | PASS | All requirements in spec.md |
| No ambiguous requirements | PASS | Checklist validated all criteria |

### II. Agentic Dev Stack Enforcement

| Step | Status | Notes |
|------|--------|-------|
| 1. Write/update specs | PASS | spec.md ratified |
| 2. Generate implementation plan | IN PROGRESS | This document |
| 3. Break into tasks | PENDING | After plan completion |
| 4. Implement tasks as defined | PENDING | After tasks generation |

### III. No Manual Coding

| Check | Status | Notes |
|-------|--------|-------|
| All code via Claude Code | REQUIRED | No manual edits permitted |
| Human provides prompts only | REQUIRED | Review and spec updates only |

### IV. Technology Constraints

| Component | Required | Planned | Status |
|-----------|----------|---------|--------|
| Frontend Framework | Next.js 16+ (App Router) | Next.js 16+ (App Router) | PASS |
| Frontend Auth | Better Auth | Better Auth | PASS |
| API Security | JWT tokens | JWT in Authorization header | PASS |
| HTTP Client | Centralized API client | lib/api.ts | PASS |
| Backend Framework | Python FastAPI | FastAPI | PASS |
| ORM | SQLModel | SQLModel | PASS |
| Database | Neon PostgreSQL | Neon PostgreSQL | PASS |
| Auth Middleware | JWT verification | python-jose verification | PASS |
| Auth Design | Backend independent | No frontend auth calls | PASS |

### V. Authentication & Security Rules

| Rule | Status | Implementation |
|------|--------|----------------|
| Better Auth frontend-only | PASS | Better Auth in Next.js only |
| JWT token issuance | PASS | Better Auth JWT plugin |
| Authorization header | PASS | Bearer token on all API requests |
| JWT signature verification | PASS | Shared BETTER_AUTH_SECRET |
| 401 on unauthenticated | PASS | HTTPBearer dependency |
| Extract user_id from token | PASS | Token sub claim |
| Task ownership enforcement | PASS | Query-level WHERE user_id |
| Never trust request body user_id | PASS | JWT is source of truth |

### VI. API Rules

| Endpoint | Method | Auth Required | Status |
|----------|--------|---------------|--------|
| /api/{user_id}/tasks | GET | Yes | PLANNED |
| /api/{user_id}/tasks | POST | Yes | PLANNED |
| /api/{user_id}/tasks/{id} | GET | Yes | PLANNED |
| /api/{user_id}/tasks/{id} | PUT | Yes | PLANNED |
| /api/{user_id}/tasks/{id} | DELETE | Yes | PLANNED |
| /api/{user_id}/tasks/{id}/complete | PATCH | Yes | PLANNED |

**Gate Result**: PASS - All constitution checks satisfied. Proceeding to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/001-fullstack-todo-app/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (OpenAPI spec)
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
backend/
├── main.py              # FastAPI app entry point
├── auth.py              # JWT verification utilities
├── database.py          # Neon PostgreSQL connection
├── models.py            # SQLModel models (User reference, Task)
├── routes/
│   └── tasks.py         # Task CRUD endpoints
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not in git)
└── CLAUDE.md            # Backend development rules

frontend/
├── app/
│   ├── layout.tsx       # Root layout with AuthProvider
│   ├── page.tsx         # Landing/redirect page
│   ├── signin/
│   │   └── page.tsx     # Sign-in form
│   ├── signup/
│   │   └── page.tsx     # Sign-up form
│   └── dashboard/
│       └── page.tsx     # Task list and management
├── components/
│   ├── auth-provider.tsx    # Better Auth session provider
│   ├── task-list.tsx        # Task display component
│   ├── task-form.tsx        # Create/edit task form
│   └── task-item.tsx        # Individual task component
├── lib/
│   ├── auth.ts          # Better Auth configuration
│   └── api.ts           # Centralized API client
├── package.json         # Node dependencies
├── .env.local           # Environment variables (not in git)
└── CLAUDE.md            # Frontend development rules
```

**Structure Decision**: Web application structure with separate frontend/ and backend/ directories following monorepo conventions defined in constitution.

## Complexity Tracking

No violations requiring justification. Implementation follows constitution-mandated technology stack exactly.

---

## Phase II Implementation Plan

### 1. Repository & Environment Setup

#### 1.1 Validate Monorepo Structure
- Confirm `/frontend` directory exists or create it
- Confirm `/backend` directory exists or create it
- Verify `/specs/001-fullstack-todo-app/` contains spec.md

#### 1.2 Environment Variables Strategy
- Frontend: `.env.local` with DATABASE_URL, BETTER_AUTH_SECRET, NEXT_PUBLIC_API_URL
- Backend: `.env` with DATABASE_URL, BETTER_AUTH_SECRET
- Shared secret BETTER_AUTH_SECRET must match exactly between services
- Document all required variables in respective CLAUDE.md files

#### 1.3 Frontend Startup Flow
- Install dependencies: `npm install`
- Start development server: `npm run dev`
- Default port: 3000
- Verify Better Auth routes work at `/api/auth/*`

#### 1.4 Backend Startup Flow
- Install dependencies: `pip install -r requirements.txt`
- Start development server: `uvicorn main:app --reload`
- Default port: 8000
- Verify health check at `/`

### 2. Database & ORM Preparation

#### 2.1 SQLModel Models
- Reference: Constitution database requirements
- Task model fields: id, user_id, title, description, completed, created_at, updated_at
- user_id is string type (Better Auth user IDs)
- Primary key: id (auto-increment integer)
- Foreign key: user_id references Better Auth users (not enforced in DB, app-level only)

#### 2.2 Neon PostgreSQL Connection
- Use async connection pool via SQLModel
- Connection string from DATABASE_URL environment variable
- Handle connection errors gracefully with retry logic
- Close connections properly on shutdown

#### 2.3 Schema Initialization
- SQLModel.metadata.create_all() on startup
- Idempotent - safe to run multiple times
- No migration framework for Phase II (direct schema sync)

#### 2.4 Indexing Strategy
- Primary index on id (automatic)
- Index on user_id for query filtering performance
- Index on (user_id, completed) for filtered list queries

### 3. Backend (FastAPI) Implementation Plan

#### 3.1 FastAPI App Bootstrap
- Create main.py with FastAPI app instance
- Configure CORS for frontend origin
- Add lifespan handler for database connection
- Include task router

#### 3.2 Route Organization
- All routes under `/api/` prefix
- Task routes: `/api/{user_id}/tasks`
- Health check: `/` or `/health`

#### 3.3 Request/Response Models
- TaskCreate: title (required), description (optional)
- TaskUpdate: title (optional), description (optional), completed (optional)
- TaskResponse: all fields including id, timestamps
- TaskListResponse: list of TaskResponse

#### 3.4 Error Handling Conventions
- HTTPException for all errors
- 400: Bad Request (validation failures)
- 401: Unauthorized (missing/invalid token)
- 403: Forbidden (user_id mismatch)
- 404: Not Found (task doesn't exist for user)
- 500: Internal Server Error (unexpected failures)

#### 3.5 Task CRUD Endpoints
- GET /api/{user_id}/tasks - List all tasks for user
- POST /api/{user_id}/tasks - Create new task
- GET /api/{user_id}/tasks/{task_id} - Get single task
- PUT /api/{user_id}/tasks/{task_id} - Update task
- DELETE /api/{user_id}/tasks/{task_id} - Delete task
- PATCH /api/{user_id}/tasks/{task_id}/complete - Toggle completion

#### 3.6 User-Based Query Filtering
- All queries include WHERE user_id = {authenticated_user_id}
- Verify route user_id matches JWT user_id before any operation
- Return 403 if user_id mismatch detected

### 4. Authentication & JWT Verification Plan

#### 4.1 Better Auth JWT Configuration (Frontend)
- Configure betterAuth with jwt plugin enabled
- Set expiresIn to 7 days
- Use BETTER_AUTH_SECRET from environment
- Enable emailAndPassword authentication

#### 4.2 JWT Extraction (Backend)
- Use FastAPI HTTPBearer security scheme
- Extract token from Authorization: Bearer {token} header
- Dependency injection via Depends(get_current_user)

#### 4.3 Signature Verification (Backend)
- Use python-jose library
- Verify with BETTER_AUTH_SECRET and HS256 algorithm
- Reject invalid signatures with 401

#### 4.4 Token Decoding and User Context
- Extract sub claim as user_id
- Extract email claim for convenience
- Return user dict with id and email
- Inject into route handlers via dependency

#### 4.5 Expired/Invalid Token Handling
- Catch JWTError exceptions
- Return 401 Unauthorized with clear message
- Frontend redirects to /signin on 401 response

### 5. Frontend (Next.js) Implementation Plan

#### 5.1 App Router Structure
- app/layout.tsx: Root layout with AuthProvider wrapper
- app/page.tsx: Landing page with redirect logic
- app/signin/page.tsx: Sign-in form (client component)
- app/signup/page.tsx: Sign-up form (client component)
- app/dashboard/page.tsx: Protected task management page

#### 5.2 Auth-Aware Layouts
- AuthProvider wraps entire app in layout.tsx
- Dashboard checks session before rendering
- Redirect unauthenticated users to /signin
- Redirect authenticated users from /signin to /dashboard

#### 5.3 Task UI Components
- TaskList: Displays all user tasks with loading state
- TaskItem: Individual task with complete toggle, edit, delete
- TaskForm: Create/edit form with title and description inputs
- EmptyState: Shown when user has no tasks

#### 5.4 Client vs Server Component Strategy
- Server components: Layout, static content
- Client components: Forms, interactive elements (marked with 'use client')
- Auth-dependent pages are client components (need session state)

#### 5.5 Responsive Design
- Mobile-first approach using Tailwind CSS
- Breakpoints: sm (640px), md (768px), lg (1024px)
- Stack layout on mobile, side-by-side on desktop
- Touch-friendly button sizes (min 44px)

### 6. API Client & Auth Integration Plan

#### 6.1 Centralized API Client Design
- lib/api.ts exports all API functions
- Single source for API_BASE configuration
- Consistent error handling across all calls
- Type-safe request/response interfaces

#### 6.2 Automatic JWT Attachment
- getAuthToken() retrieves token from Better Auth session
- All API requests include Authorization: Bearer {token}
- Token refresh handled by Better Auth automatically

#### 6.3 Error Handling for 401/403
- 401: Redirect to /signin (token expired/invalid)
- 403: Show error message (access denied)
- 404: Show "not found" message
- 500: Show generic error with retry option

#### 6.4 Logout Handling
- Call auth.api.signOut() on logout click
- Clear local session state
- Redirect to /signin
- API client throws if no session available

### 7. Security & Authorization Enforcement

#### 7.1 User ID Matching
- Route parameter {user_id} must match JWT sub claim
- Verified in every endpoint before any operation
- Return 403 Forbidden on mismatch

#### 7.2 Task Ownership Enforcement
- Every query filters by user_id
- SELECT ... WHERE user_id = ?
- UPDATE ... WHERE id = ? AND user_id = ?
- DELETE ... WHERE id = ? AND user_id = ?

#### 7.3 Cross-User Access Prevention
- User A cannot see User B's tasks
- User A cannot modify User B's tasks
- URL manipulation returns 403 or 404
- No user enumeration via error messages

#### 7.4 Secret Management
- BETTER_AUTH_SECRET in .env files only
- .env and .env.local in .gitignore
- Document required variables in CLAUDE.md
- Minimum 32 character secret length

### 8. Testing & Validation Strategy

#### 8.1 Manual Validation Checklist

**Authentication Flow**
- [ ] Create new account with email/password
- [ ] Sign in with valid credentials
- [ ] Session persists across page refresh
- [ ] Sign out terminates session
- [ ] Invalid credentials show error message

**Task CRUD Operations**
- [ ] View empty state when no tasks
- [ ] Create task with title only
- [ ] Create task with title and description
- [ ] Edit task title
- [ ] Edit task description
- [ ] Delete task with confirmation
- [ ] Task changes persist after refresh

**Task Completion**
- [ ] Mark task as complete (visual indicator)
- [ ] Mark task as incomplete (indicator removed)
- [ ] Completion status persists after refresh

**User Isolation**
- [ ] User A's tasks not visible to User B
- [ ] Direct URL to User B's task returns error
- [ ] API request for User B's data rejected

#### 8.2 Auth Edge Cases
- [ ] Expired token redirects to signin
- [ ] Missing token returns 401
- [ ] Malformed token returns 401
- [ ] Wrong secret returns 401

#### 8.3 Task Isolation Verification
- [ ] Create tasks as User A
- [ ] Sign out, sign in as User B
- [ ] Verify User A's tasks not visible
- [ ] Attempt API call to User A's endpoint
- [ ] Verify 403 response

#### 8.4 API Error Scenarios
- [ ] Create task without title (400)
- [ ] Get non-existent task (404)
- [ ] Update non-existent task (404)
- [ ] Delete non-existent task (404)
- [ ] Title exceeds 200 chars (400)
- [ ] Description exceeds 2000 chars (400)

### 9. Deployment Readiness Checklist

#### 9.1 Environment Variables

**Frontend (.env.local)**
- [ ] DATABASE_URL set
- [ ] BETTER_AUTH_SECRET set (32+ chars)
- [ ] NEXT_PUBLIC_API_URL set to backend URL

**Backend (.env)**
- [ ] DATABASE_URL set
- [ ] BETTER_AUTH_SECRET set (matches frontend)

#### 9.2 Production Safety
- [ ] Debug mode disabled
- [ ] CORS configured for production origin
- [ ] HTTPS enforced
- [ ] Secrets not in git history
- [ ] Error messages don't leak internals

#### 9.3 Compatibility Validation
- [ ] Frontend can reach backend API
- [ ] JWT tokens accepted by backend
- [ ] Database connections successful
- [ ] All CRUD operations work end-to-end

#### 9.4 Phase III Extension Readiness
- [ ] API structure supports additional endpoints
- [ ] User context available for future features
- [ ] Database schema can be extended
- [ ] No tight coupling preventing chatbot addition

---

## Artifacts to Generate

After this plan is approved:

1. **research.md** - Document technology decisions and alternatives considered
2. **data-model.md** - Entity definitions with fields and relationships
3. **contracts/** - OpenAPI specification for all endpoints
4. **quickstart.md** - Setup and run instructions
5. **tasks.md** - Atomic implementation tasks (via /sp.tasks)
