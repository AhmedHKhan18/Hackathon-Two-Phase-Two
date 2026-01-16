# Tasks: AI-Powered Todo Chatbot

**Input**: Design documents from `/specs/002-ai-todo-chatbot/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), agent-spec.md, mcp-tools-spec.md, data-model.md, contracts/chat-api.yaml

**Tests**: Manual validation only for Phase III (no automated tests required per spec)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/` (Python FastAPI), `frontend/` (Next.js TypeScript)
- **New modules**: `backend/mcp/`, `backend/agent/`, `backend/chat/`
- Paths follow structure defined in plan.md

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Prepare development environment for Phase III by adding required dependencies

**Prerequisites**: Phase II backend operational

- [ ] T001 Verify existing monorepo structure (backend/, frontend/, specs/) intact from Phase II
- [ ] T002 Add Phase III dependencies to backend (openai-agents, mcp) via uv add or pip install
- [ ] T003 [P] Add OPENAI_API_KEY to backend/.env.example
- [ ] T004 [P] Create backend/mcp/__init__.py module directory
- [ ] T005 [P] Create backend/agent/__init__.py module directory
- [ ] T006 [P] Create backend/chat/__init__.py module directory
- [ ] T007 Verify imports work: `import openai_agents` and `import mcp` succeed

---

## Phase 2: Database & ORM Setup

**Purpose**: Extend database schema with Conversation and Message tables while preserving existing Task table

**Prerequisites**: Phase 1 complete

### Schema Extension

- [ ] T008 Define MessageRole enum (user, assistant) in backend/models.py
- [ ] T009 Define Conversation SQLModel in backend/models.py per data-model.md
  - Fields: id, user_id, created_at, updated_at
  - Indexes: user_id, (user_id, updated_at)
- [ ] T010 Define Message SQLModel in backend/models.py per data-model.md
  - Fields: id, conversation_id, user_id, role, content, created_at
  - Foreign Key: conversation_id → conversation.id (CASCADE)
  - Indexes: conversation_id, (conversation_id, created_at), user_id
- [ ] T011 Add SQLModel relationships: Conversation.messages ↔ Message.conversation
- [ ] T012 Run database migration to create conversation and message tables
- [ ] T013 Verify schema: tables exist, columns correct, indexes present, foreign keys work

**Checkpoint**: Database ready with Conversation and Message tables

---

## Phase 3: MCP Server Implementation

**Purpose**: Implement MCP Server exposing five task management tools that operate statelessly against the database

**Prerequisites**: Phase 2 complete (database models exist)

### MCP Server Core

- [ ] T014 Create MCP server initialization in backend/mcp/server.py
  - Server name: todo-mcp-server
  - Import Server from mcp.server

### MCP Tools Implementation

- [ ] T015 [P] Implement add_task tool in backend/mcp/tools.py
  - Inputs: user_id (required), title (required), description (optional)
  - Output: { status, task_id, title, message }
  - Validation: title required, max 200 chars; description max 2000 chars
  - Database: INSERT into task table
- [ ] T016 [P] Implement list_tasks tool in backend/mcp/tools.py
  - Inputs: user_id (required), status (optional: all/pending/completed)
  - Output: { status, count, tasks[] }
  - Filtering: by completion status when specified
  - Ordering: created_at descending
- [ ] T017 [P] Implement complete_task tool in backend/mcp/tools.py
  - Inputs: user_id (required), task_id (required)
  - Output: { status, task_id, title, completed, message }
  - Validation: task must exist and belong to user
  - Database: UPDATE task SET completed = true
- [ ] T018 [P] Implement delete_task tool in backend/mcp/tools.py
  - Inputs: user_id (required), task_id (required)
  - Output: { status, task_id, title, message }
  - Validation: task must exist and belong to user
  - Database: DELETE from task table
- [ ] T019 [P] Implement update_task tool in backend/mcp/tools.py
  - Inputs: user_id (required), task_id (required), title (optional), description (optional)
  - Output: { status, task_id, title, description, message }
  - Validation: at least one field required; field length limits
  - Database: UPDATE task with provided fields

### MCP Server Registration

- [ ] T020 Register all five tools with MCP server in backend/mcp/server.py
  - Include tool descriptions for agent per mcp-tools-spec.md
- [ ] T021 Enforce user isolation: all tools include user_id in database queries
  - Pattern: WHERE user_id = :user_id in all queries
  - Return "Task not found" for unauthorized access (no info leakage)

**Checkpoint**: MCP Server ready with all five tools registered and tested

---

## Phase 4: AI Agent Implementation

**Purpose**: Configure OpenAI Agent with system prompt and MCP tool registration for natural language task management

**Prerequisites**: Phase 3 complete (MCP tools available)

### Agent Configuration

- [ ] T022 Create agent module initialization in backend/agent/__init__.py
- [ ] T023 Define system prompt in backend/agent/prompts.py per agent-spec.md
  - Include capabilities, rules, examples, constraints
- [ ] T024 Create agent configuration in backend/agent/config.py
  - Model: gpt-4o (configurable)
  - Temperature: 0.7
  - Max Tokens: 1000

### Agent Execution

- [ ] T025 Create agent runner function in backend/agent/runner.py
  - Input: user message, conversation history, user_id
  - Output: agent response, tool calls executed
- [ ] T026 Register MCP tools with agent via OpenAI Agents SDK in backend/agent/runner.py
- [ ] T027 Implement tool call execution flow in backend/agent/runner.py
  - Agent requests tool → Execute tool → Return result to agent
  - Inject user_id into all tool calls
- [ ] T028 Verify agent constraint: no direct database imports in agent module

**Checkpoint**: Agent ready to interpret natural language and call MCP tools

---

## Phase 5: User Story 1 - Basic Task Creation via Chat (Priority: P1)

**Goal**: Users can create tasks by typing natural language commands

**Independent Test**: Send "Add a task to buy groceries", verify task appears in database

### Chat API Core

- [ ] T029 Create chat router in backend/chat/router.py with prefix /api/{user_id}
- [ ] T030 Define ChatRequest Pydantic schema in backend/chat/schemas.py
  - Fields: message (required, max 2000), conversation_id (optional)
- [ ] T031 Define ChatResponse Pydantic schema in backend/chat/schemas.py
  - Fields: conversation_id, response, tool_calls[]
- [ ] T032 Implement POST /api/{user_id}/chat endpoint in backend/chat/router.py
  - Flow: Validate → Load history → Store user message → Run agent → Store response → Return
- [ ] T033 Register chat router in backend/main.py

### Conversation Services

- [ ] T034 Implement conversation creation service in backend/chat/services.py
  - Create new conversation when conversation_id not provided
- [ ] T035 Implement conversation loading service in backend/chat/services.py
  - Load most recent 100 messages for conversation_id
  - Order by created_at ascending

### Message Services

- [ ] T036 Implement user message storage service in backend/chat/services.py
  - Store before agent execution
  - Fields: conversation_id, user_id, role=user, content, created_at
- [ ] T037 Implement assistant message storage service in backend/chat/services.py
  - Store after agent execution completes
  - Fields: conversation_id, user_id, role=assistant, content, created_at

### Agent Integration

- [ ] T038 Connect chat endpoint to agent runner in backend/chat/router.py
  - Pass message history, user message, user_id
  - Capture response and tool calls

**Checkpoint**: Users can create tasks via natural language. US1 testable: "Add a task to buy groceries" creates task.

---

## Phase 6: User Story 2 - List and Query Tasks via Chat (Priority: P2)

**Goal**: Users can ask about their tasks using natural language

**Independent Test**: Create tasks, ask "Show me all my tasks", verify response lists all tasks

### Implementation

- [ ] T039 [US2] Verify list_tasks tool responds correctly to agent calls
- [ ] T040 [US2] Test agent interprets "Show me all my tasks" → list_tasks(status="all")
- [ ] T041 [US2] Test agent interprets "What's pending?" → list_tasks(status="pending")
- [ ] T042 [US2] Test agent interprets "What have I completed?" → list_tasks(status="completed")
- [ ] T043 [US2] Verify agent formats task list response per agent-spec.md formatting rules

**Checkpoint**: Users can query tasks via natural language. US2 testable independently.

---

## Phase 7: User Story 3 - Complete Tasks via Chat (Priority: P3)

**Goal**: Users can mark tasks as complete using natural language

**Independent Test**: Create task, say "Mark task 1 as complete", verify status changes

### Implementation

- [ ] T044 [US3] Verify complete_task tool responds correctly to agent calls
- [ ] T045 [US3] Test agent interprets "Mark task 3 as complete" → complete_task(task_id=3)
- [ ] T046 [US3] Test agent chains list_tasks → complete_task for title references
  - "Complete the groceries task" → list first, then complete
- [ ] T047 [US3] Verify agent confirms completion in natural language

**Checkpoint**: Users can complete tasks via natural language. US3 testable independently.

---

## Phase 8: User Story 4 - Delete Tasks via Chat (Priority: P4)

**Goal**: Users can remove tasks using natural language

**Independent Test**: Create task, say "Delete task 1", verify removal

### Implementation

- [ ] T048 [US4] Verify delete_task tool responds correctly to agent calls
- [ ] T049 [US4] Test agent interprets "Delete task 5" → delete_task(task_id=5)
- [ ] T050 [US4] Test agent chains list_tasks → delete_task for title references
  - "Delete the meeting task" → list first, then delete
- [ ] T051 [US4] Verify agent confirms deletion in natural language

**Checkpoint**: Users can delete tasks via natural language. US4 testable independently.

---

## Phase 9: User Story 5 - Update Tasks via Chat (Priority: P5)

**Goal**: Users can modify task details using natural language

**Independent Test**: Create task, say "Change task 1 to call mom tonight", verify update

### Implementation

- [ ] T052 [US5] Verify update_task tool responds correctly to agent calls
- [ ] T053 [US5] Test agent interprets "Change task 1 to call mom tonight" → update_task(task_id=1, title="call mom tonight")
- [ ] T054 [US5] Test agent interprets "Update task 2 description to include charts" → update_task(task_id=2, description="include charts")
- [ ] T055 [US5] Verify agent asks for missing info: "Rename task 2 to something better" → asks for new title

**Checkpoint**: Users can update tasks via natural language. US5 testable independently.

---

## Phase 10: User Story 6 - Conversation Persistence (Priority: P6)

**Goal**: Chat history persists across sessions

**Independent Test**: Send messages, refresh page, verify previous messages appear

### Conversation Persistence

- [ ] T056 [US6] Update conversation.updated_at after each message in backend/chat/services.py
- [ ] T057 [US6] Verify stateless operation: no module-level conversation state
- [ ] T058 [US6] Test server restart does not affect conversation continuity

### Conversation Management Endpoints

- [ ] T059 [US6] Implement GET /api/{user_id}/conversations endpoint in backend/chat/router.py
  - Response: list of conversations with preview and timestamps
- [ ] T060 [US6] Implement GET /api/{user_id}/conversations/{id} endpoint in backend/chat/router.py
  - Response: full conversation with all messages
- [ ] T061 [US6] Implement DELETE /api/{user_id}/conversations/{id} endpoint in backend/chat/router.py
  - Behavior: cascade delete conversation and all messages

**Checkpoint**: Conversations persist across sessions. US6 testable independently.

---

## Phase 11: Authentication Integration

**Purpose**: Ensure chat endpoints are protected with JWT authentication

**Prerequisites**: Phase II authentication working

### Backend Authentication

- [ ] T062 Verify existing JWT middleware operational in backend/auth.py
- [ ] T063 Apply JWT dependency to all chat endpoints in backend/chat/router.py
  - Unauthenticated requests return 401
- [ ] T064 Extract user_id from JWT sub claim in backend/chat/router.py
- [ ] T065 Validate URL {user_id} matches JWT user_id
  - Return 403 Forbidden if mismatch
- [ ] T066 Pass authenticated user_id to agent runner and MCP tools
- [ ] T067 Verify conversation ownership: conversation belongs to authenticated user
  - Return 404 if not found or unauthorized

**Checkpoint**: All chat endpoints protected with JWT authentication

---

## Phase 12: Frontend Integration

**Purpose**: Set up chat UI to communicate with backend chat API

**Prerequisites**: Phase 5 and Phase 6 complete

### Chat Page Setup

- [ ] T068 Create chat page in frontend/app/chat/page.tsx
  - Components: message list, input field, send button
- [ ] T069 Implement chat API client in frontend/lib/api.ts
  - Function: sendChatMessage(userId, message, conversationId?)
  - Attach JWT token to requests

### Chat Components

- [ ] T070 [P] Create ChatMessages component in frontend/components/chat-messages.tsx
  - User/assistant message styling
  - Timestamps
  - Loading states
- [ ] T071 [P] Create ChatInput component in frontend/components/chat-input.tsx
  - Text input, send button, enter key submit
  - Validation: max 2000 characters
- [ ] T072 [P] Create ConversationList component in frontend/components/conversation-list.tsx
  - Show user's conversations
  - Allow switching between conversations

### Chat State Management

- [ ] T073 Implement conversation state in frontend/app/chat/page.tsx
  - Current conversation_id, message list, loading state
  - Flow: send message → show loading → display response
- [ ] T074 Implement conversation loading on page mount
  - Fetch existing conversations
  - Load selected conversation messages
- [ ] T075 Handle error states in chat UI
  - Network errors, auth errors, validation errors

### Navigation

- [ ] T076 Add chat link to dashboard navigation in frontend/app/dashboard/page.tsx
- [ ] T077 Add dashboard link to chat navigation in frontend/app/chat/page.tsx

**Checkpoint**: Frontend chat UI complete and connected to backend

---

## Phase 13: Error Handling & Validation

**Purpose**: Implement comprehensive error handling for all failure modes

**Prerequisites**: Phases 5-12 complete

### Input Validation

- [ ] T078 [P] Validate chat message: required, max 2000 chars in backend/chat/router.py
- [ ] T079 [P] Validate conversation_id format in backend/chat/router.py

### Error Scenarios

- [ ] T080 [P] Handle task not found in MCP tools gracefully
  - Agent responds: "I couldn't find task #[ID]"
- [ ] T081 [P] Handle empty task list scenario
  - Agent responds: "You don't have any tasks yet"
- [ ] T082 [P] Handle invalid task ID format
  - Return clear error for non-integer task IDs
- [ ] T083 Handle ambiguous intent: agent asks for clarification per agent-spec.md
- [ ] T084 Handle OpenAI API errors gracefully
  - Rate limits, timeouts, service unavailable
  - Return user-friendly message without technical details
- [ ] T085 Handle database errors gracefully
  - Generic error message, log details server-side
- [ ] T086 Handle MCP tool execution errors
  - Agent reports errors in friendly terms

**Checkpoint**: All error cases handled gracefully with user-friendly messages

---

## Phase 14: Testing & Verification

**Purpose**: Verify all functionality through systematic testing

**Prerequisites**: Phases 1-13 complete

### Natural Language Pattern Testing

- [ ] T087 Test task creation commands:
  - "Add a task to buy groceries"
  - "I need to call mom"
  - "Add task: finish report with description needs charts"
- [ ] T088 Test task listing commands:
  - "Show me all my tasks"
  - "What's pending?"
  - "What have I completed?"
- [ ] T089 Test task completion commands:
  - "Mark task 3 as complete"
  - "I finished the groceries task"
  - "Complete task 999" (not found)
- [ ] T090 Test task deletion commands:
  - "Delete task 5"
  - "Delete the meeting task"
  - "Delete task 999" (not found)
- [ ] T091 Test task update commands:
  - "Change task 1 to call mom tonight"
  - "Update task 2 description to include charts"

### System Testing

- [ ] T092 Test conversation continuity across messages
  - "also add milk" understands prior context
- [ ] T093 Test stateless behavior: restart server, continue conversation
- [ ] T094 Test tool chaining: "Complete the groceries task" (list → complete)
- [ ] T095 Test user isolation: User A cannot see User B's tasks
- [ ] T096 Test edge cases: ambiguous references, empty list, invalid IDs

**Checkpoint**: All test scenarios pass, system meets acceptance criteria

---

## Phase 15: Deployment Preparation

**Purpose**: Prepare system for production deployment

**Prerequisites**: Phase 14 complete (all tests pass)

### Environment Configuration

- [ ] T097 [P] Verify all environment variables documented in .env.example
  - DATABASE_URL, BETTER_AUTH_SECRET, OPENAI_API_KEY
- [ ] T098 [P] Configure CORS for production frontend domains in backend/main.py

### Deployment

- [ ] T099 Verify Neon PostgreSQL connection works from deployment environment
- [ ] T100 Deploy backend to hosting platform (Railway/Render/Vercel)
- [ ] T101 Deploy frontend to Vercel
- [ ] T102 Test full flow in production: Auth → Chat → Task operations → Persistence

**Checkpoint**: System deployed and functional in production

---

## Phase 16: Documentation & Deliverables

**Purpose**: Create comprehensive documentation for hackathon submission

**Prerequisites**: All previous phases complete

### Documentation

- [ ] T103 [P] Update README.md with Phase III overview, setup, and usage
- [ ] T104 [P] Document architecture with diagrams in README or separate doc
- [ ] T105 [P] Verify OpenAPI spec complete in specs/002-ai-todo-chatbot/contracts/chat-api.yaml
- [ ] T106 [P] Document supported natural language commands with examples
- [ ] T107 Create demo script for hackathon judges

### Final Verification

- [ ] T108 Verify repository structure meets hackathon requirements
- [ ] T109 Run final manual validation checklist

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - can start immediately
- **Phase 2 (Database)**: Depends on Phase 1
- **Phase 3 (MCP Server)**: Depends on Phase 2
- **Phase 4 (AI Agent)**: Depends on Phase 3
- **Phase 5 (US1 - Task Creation)**: Depends on Phase 4
- **Phases 6-10 (US2-US6)**: Depend on Phase 5
- **Phase 11 (Authentication)**: Can start after Phase 5, parallel to US2-US6
- **Phase 12 (Frontend)**: Depends on Phase 5
- **Phase 13 (Error Handling)**: Depends on Phases 5-12
- **Phase 14 (Testing)**: Depends on Phase 13
- **Phase 15 (Deployment)**: Depends on Phase 14
- **Phase 16 (Documentation)**: Can start partially in parallel

### User Story Dependencies

- **US1 (P1)**: Foundation for all other stories - must complete first
- **US2-US6 (P2-P6)**: All depend on US1, can proceed sequentially

### Parallel Opportunities

**Phase 1 (Setup)**:
```
T003, T004, T005, T006 (env, modules)
```

**Phase 3 (MCP Tools)**:
```
T015, T016, T017, T018, T019 (all five tools)
```

**Phase 12 (Frontend)**:
```
T070, T071, T072 (chat components)
```

**Phase 13 (Error Handling)**:
```
T078, T079, T080, T081, T082 (validation and error scenarios)
```

**Phase 16 (Documentation)**:
```
T103, T104, T105, T106 (all docs)
```

---

## Implementation Strategy

### MVP First (US1-US2 Only)

1. Complete Phases 1-4: Setup, Database, MCP, Agent
2. Complete Phase 5: User Story 1 (Task Creation)
3. Complete Phase 6: User Story 2 (Task Listing)
4. **STOP and VALIDATE**: Test task creation and listing via chat
5. Deploy/demo if ready - users can create and view tasks via conversation

### Incremental Delivery

1. Phases 1-4 → Infrastructure ready
2. Add US1 → Test task creation → MVP Chat!
3. Add US2 → Test task listing → Can see tasks
4. Add US3 → Test completion → Progress tracking
5. Add US4 → Test deletion → Full CRUD
6. Add US5 → Test updates → Refinement
7. Add US6 → Test persistence → Session continuity
8. Auth + Frontend + Polish → Production ready

---

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 109 |
| Phase 1 (Setup) | 7 tasks |
| Phase 2 (Database) | 6 tasks |
| Phase 3 (MCP Server) | 8 tasks |
| Phase 4 (AI Agent) | 7 tasks |
| Phase 5 (US1 - Create) | 10 tasks |
| Phase 6 (US2 - List) | 5 tasks |
| Phase 7 (US3 - Complete) | 4 tasks |
| Phase 8 (US4 - Delete) | 4 tasks |
| Phase 9 (US5 - Update) | 4 tasks |
| Phase 10 (US6 - Persist) | 6 tasks |
| Phase 11 (Auth) | 6 tasks |
| Phase 12 (Frontend) | 10 tasks |
| Phase 13 (Errors) | 9 tasks |
| Phase 14 (Testing) | 10 tasks |
| Phase 15 (Deploy) | 6 tasks |
| Phase 16 (Docs) | 7 tasks |
| Parallel Opportunities | 25+ tasks marked [P] |
| MVP Tasks | ~43 tasks (through US2) |

---

## Notes

- [P] tasks = different files, no dependencies within that batch
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- No automated tests for Phase III (manual validation per spec)
- All API endpoints require JWT authentication except health check
- Agent MUST NEVER access database directly - only via MCP tools
- All conversation state in database - server is stateless
