# Tasks: Full-Stack Todo Web Application

**Input**: Design documents from `/specs/001-fullstack-todo-app/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/openapi.yaml

**Tests**: Manual validation only for Phase II (no automated tests required per spec)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/` (Python FastAPI), `frontend/` (Next.js TypeScript)
- Paths follow structure defined in plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and monorepo structure

- [x] T001 Create monorepo directory structure (backend/, frontend/)
- [x] T002 [P] Initialize Python backend with FastAPI in backend/requirements.txt
- [x] T003 [P] Initialize Next.js frontend with TypeScript in frontend/package.json
- [x] T004 [P] Create backend/.env.example with required environment variables
- [x] T005 [P] Create frontend/.env.example with required environment variables
- [x] T006 [P] Create backend/CLAUDE.md with backend development rules
- [x] T007 [P] Create frontend/CLAUDE.md with frontend development rules
- [x] T008 Add .gitignore entries for .env, .env.local, node_modules, __pycache__, venv

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

### Backend Foundation

- [x] T009 Create database connection module in backend/database.py (Neon PostgreSQL via SQLModel)
- [x] T010 Create Task SQLModel in backend/models.py per data-model.md
- [x] T011 Create JWT verification utilities in backend/auth.py (python-jose, HS256, BETTER_AUTH_SECRET)
- [x] T012 Create FastAPI app entry point in backend/main.py with CORS and lifespan handler
- [x] T013 Create task routes file structure in backend/routes/tasks.py (empty router)

### Frontend Foundation

- [x] T014 Configure Better Auth with JWT plugin in frontend/lib/auth.ts
- [x] T015 Create Better Auth API route handler in frontend/app/api/auth/[...all]/route.ts
- [x] T016 Create centralized API client in frontend/lib/api.ts with JWT attachment
- [x] T017 Create AuthProvider component in frontend/components/auth-provider.tsx
- [x] T018 Create root layout with AuthProvider in frontend/app/layout.tsx
- [x] T019 Configure Tailwind CSS in frontend/tailwind.config.ts and frontend/app/globals.css

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - User Registration and Authentication (Priority: P1)

**Goal**: Users can create accounts, sign in, maintain sessions, and sign out securely

**Independent Test**: Create new account, sign in, refresh page (session persists), sign out

### Implementation for User Story 1

- [x] T020 [US1] Create sign-up page with email/password form in frontend/app/signup/page.tsx
- [x] T021 [US1] Create sign-in page with email/password form in frontend/app/signin/page.tsx
- [x] T022 [US1] Create landing page with redirect logic in frontend/app/page.tsx
- [x] T023 [US1] Implement session persistence check and redirect in frontend/app/dashboard/page.tsx (skeleton)
- [x] T024 [US1] Add sign-out button component in frontend/components/sign-out-button.tsx
- [x] T025 [US1] Add error message display for invalid credentials on sign-in page
- [x] T026 [US1] Add success redirect to dashboard after registration/sign-in

**Checkpoint**: Users can register, sign in, refresh (session persists), and sign out. US1 fully testable.

---

## Phase 4: User Story 2 - View and Create Tasks (Priority: P2)

**Goal**: Authenticated users can view their task list and create new tasks

**Independent Test**: Sign in, view empty state, create tasks, verify they appear in list

### Backend Implementation for User Story 2

- [x] T027 [US2] Implement GET /api/{user_id}/tasks endpoint in backend/routes/tasks.py
- [x] T028 [US2] Implement POST /api/{user_id}/tasks endpoint in backend/routes/tasks.py
- [x] T029 [US2] Add user_id validation (JWT sub must match route user_id) in backend/routes/tasks.py
- [x] T030 [US2] Add request validation for TaskCreate schema (title required, max lengths) in backend/routes/tasks.py

### Frontend Implementation for User Story 2

- [x] T031 [P] [US2] Create TaskList component in frontend/components/task-list.tsx
- [x] T032 [P] [US2] Create TaskItem component in frontend/components/task-item.tsx
- [x] T033 [P] [US2] Create TaskForm component (create mode) in frontend/components/task-form.tsx
- [x] T034 [P] [US2] Create EmptyState component in frontend/components/empty-state.tsx
- [x] T035 [US2] Add API functions for listTasks and createTask in frontend/lib/api.ts
- [x] T036 [US2] Integrate task list and create form into dashboard page in frontend/app/dashboard/page.tsx
- [x] T037 [US2] Add validation error display for missing title on task form

**Checkpoint**: Users can view empty state, create tasks with title/description, see tasks in list. US2 fully testable.

---

## Phase 5: User Story 3 - Update and Delete Tasks (Priority: P3)

**Goal**: Authenticated users can edit task details and delete tasks

**Independent Test**: Create task, edit title/description, verify changes persist, delete task, confirm removal

### Backend Implementation for User Story 3

- [x] T038 [US3] Implement GET /api/{user_id}/tasks/{task_id} endpoint in backend/routes/tasks.py
- [x] T039 [US3] Implement PUT /api/{user_id}/tasks/{task_id} endpoint in backend/routes/tasks.py
- [x] T040 [US3] Implement DELETE /api/{user_id}/tasks/{task_id} endpoint in backend/routes/tasks.py
- [x] T041 [US3] Add 404 handling for non-existent tasks in backend/routes/tasks.py

### Frontend Implementation for User Story 3

- [x] T042 [US3] Add edit mode to TaskForm component in frontend/components/task-form.tsx
- [x] T043 [US3] Add edit and delete actions to TaskItem component in frontend/components/task-item.tsx
- [x] T044 [US3] Add API functions for getTask, updateTask, deleteTask in frontend/lib/api.ts
- [x] T045 [US3] Add delete confirmation dialog in frontend/components/task-item.tsx
- [x] T046 [US3] Integrate edit/delete functionality into dashboard in frontend/app/dashboard/page.tsx

**Checkpoint**: Users can edit task title/description, delete tasks with confirmation, changes persist. US3 fully testable.

---

## Phase 6: User Story 4 - Mark Tasks Complete/Incomplete (Priority: P4)

**Goal**: Authenticated users can mark tasks as complete or incomplete to track progress

**Independent Test**: Create task, mark complete (visual indicator), mark incomplete again

### Backend Implementation for User Story 4

- [x] T047 [US4] Implement PATCH /api/{user_id}/tasks/{task_id}/complete endpoint in backend/routes/tasks.py

### Frontend Implementation for User Story 4

- [x] T048 [US4] Add completion toggle to TaskItem component with visual indicator in frontend/components/task-item.tsx
- [x] T049 [US4] Add API function for toggleTaskComplete in frontend/lib/api.ts
- [x] T050 [US4] Add visual distinction for completed vs incomplete tasks (strikethrough, opacity) in frontend/components/task-item.tsx

**Checkpoint**: Users can toggle task completion, visual indicator changes, status persists. US4 fully testable.

---

## Phase 7: User Story 5 - User Data Isolation (Priority: P5)

**Goal**: Ensure complete data isolation between users - no cross-user data access

**Independent Test**: Create tasks as User A, sign out, sign in as User B, verify A's tasks invisible

### Backend Implementation for User Story 5

- [x] T051 [US5] Enforce user_id WHERE clause on all task queries in backend/routes/tasks.py
- [x] T052 [US5] Return 403 Forbidden when JWT user_id doesn't match route user_id in backend/routes/tasks.py
- [x] T053 [US5] Ensure 404 (not 403) when accessing non-existent task to prevent user enumeration in backend/routes/tasks.py

### Frontend Implementation for User Story 5

- [x] T054 [US5] Handle 401 responses with redirect to sign-in in frontend/lib/api.ts
- [x] T055 [US5] Handle 403 responses with access denied message in frontend/lib/api.ts
- [x] T056 [US5] Ensure user_id in API calls comes from session, not URL manipulation in frontend/lib/api.ts

**Checkpoint**: User A cannot see User B's tasks, unauthenticated requests rejected, URL manipulation fails. US5 fully testable.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and validation

- [x] T057 [P] Add loading states to all data fetching operations in frontend/app/dashboard/page.tsx
- [x] T058 [P] Add error boundary for unexpected errors in frontend/app/error.tsx
- [x] T059 [P] Add responsive styling for mobile (320px) to desktop (1920px) in frontend/components/
- [x] T060 [P] Verify CORS configuration allows frontend origin in backend/main.py
- [x] T061 [P] Add health check endpoint (/) in backend/main.py
- [ ] T062 Run quickstart.md validation - verify all setup steps work
- [ ] T063 Run full manual validation checklist from plan.md section 8.1

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can proceed sequentially in priority order (P1 -> P2 -> P3 -> P4 -> P5)
  - Some parallelization possible within each story phase
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Depends on US1 (authentication required to access dashboard)
- **User Story 3 (P3)**: Depends on US2 (must have tasks to edit/delete)
- **User Story 4 (P4)**: Depends on US2 (must have tasks to mark complete)
- **User Story 5 (P5)**: Depends on US1 (requires multiple user accounts to test isolation)

### Within Each User Story

- Backend endpoints before frontend integration
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**:
```
T002, T003 (backend/frontend init)
T004, T005 (env examples)
T006, T007 (CLAUDE.md files)
```

**Phase 2 (Foundational)**:
```
After T009: T010, T011 (models, auth)
After T014: T015, T016, T017 (auth routes, api client, provider)
```

**Phase 4 (US2 Frontend)**:
```
T031, T032, T033, T034 (all components)
```

**Phase 8 (Polish)**:
```
T057, T058, T059, T060, T061 (all independent)
```

---

## Implementation Strategy

### MVP First (User Stories 1-2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Authentication)
4. Complete Phase 4: User Story 2 (View/Create Tasks)
5. **STOP and VALIDATE**: Test US1 + US2 together
6. Deploy/demo if ready - users can register and manage basic tasks

### Incremental Delivery

1. Setup + Foundational -> Foundation ready
2. Add User Story 1 -> Test auth independently -> Users can sign in
3. Add User Story 2 -> Test view/create tasks -> MVP ready!
4. Add User Story 3 -> Test edit/delete -> Full CRUD
5. Add User Story 4 -> Test completion toggle -> Progress tracking
6. Add User Story 5 -> Test isolation -> Production security
7. Polish -> Professional UX

### Suggested MVP Scope

**Minimum Viable Product**: Phase 1 + Phase 2 + Phase 3 (US1) + Phase 4 (US2)
- Users can register and sign in
- Users can create and view tasks
- ~36 tasks to MVP

---

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 63 |
| Phase 1 (Setup) | 8 tasks |
| Phase 2 (Foundational) | 11 tasks |
| Phase 3 (US1 - Auth) | 7 tasks |
| Phase 4 (US2 - View/Create) | 11 tasks |
| Phase 5 (US3 - Update/Delete) | 9 tasks |
| Phase 6 (US4 - Complete) | 4 tasks |
| Phase 7 (US5 - Isolation) | 6 tasks |
| Phase 8 (Polish) | 7 tasks |
| Parallel Opportunities | 16 tasks marked [P] |
| MVP Tasks | 36 tasks (through US2) |

---

## Notes

- [P] tasks = different files, no dependencies within that batch
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- No automated tests for Phase II (manual validation per spec)
- All API endpoints require JWT authentication except health check
