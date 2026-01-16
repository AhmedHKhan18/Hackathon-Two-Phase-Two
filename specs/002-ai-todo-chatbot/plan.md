# Implementation Plan: AI-Powered Todo Chatbot

**Feature Branch**: `002-ai-todo-chatbot`
**Created**: 2026-01-15
**Status**: Draft
**Phase**: Phase III - AI Chatbot Integration
**Plan Version**: 1.0

## Plan Overview

This document provides a detailed, ordered implementation plan for Phase III of the Todo AI Chatbot. The plan is designed for execution entirely via Claude Code following the Agentic Dev Stack workflow.

**Key Principles**:
- Each step is atomic and verifiable
- No manual coding required
- Claude Code executes all steps
- Database is the single source of truth
- All components remain stateless

---

## Dependency Graph

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              PHASE 1                                         │
│                        Project Initialization                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              PHASE 2                                         │
│                        Database & ORM Setup                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
┌───────────────────────────────┐   ┌───────────────────────────────┐
│          PHASE 3              │   │          PHASE 4              │
│       MCP Server Design       │   │      AI Agent Design          │
└───────────────────────────────┘   └───────────────────────────────┘
                    │                               │
                    └───────────────┬───────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              PHASE 5                                         │
│                       Chat API Implementation                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              PHASE 6                                         │
│                      Conversation Persistence                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
┌───────────────────────────────┐   ┌───────────────────────────────┐
│          PHASE 7              │   │          PHASE 8              │
│    Frontend Integration       │   │  Authentication Integration   │
└───────────────────────────────┘   └───────────────────────────────┘
                    │                               │
                    └───────────────┬───────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              PHASE 9                                         │
│                     Error Handling & Validation                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              PHASE 10                                        │
│                        Testing & Verification                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              PHASE 11                                        │
│                       Deployment Preparation                                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              PHASE 12                                        │
│                     Documentation & Deliverables                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Project Initialization

**Objective**: Prepare the development environment for Phase III by adding required dependencies to the existing Phase II monorepo structure.

**Prerequisites**: Phase II backend operational

**Verification**: All dependencies installed, imports resolve correctly

### Step 1.1: Verify Existing Project Structure

| Item | Description |
|------|-------------|
| Action | Confirm monorepo structure exists from Phase II |
| Directories | `/frontend`, `/backend`, `/specs` |
| Gate | All directories present and Phase II code intact |

### Step 1.2: Add Phase III Dependencies to Backend

| Item | Description |
|------|-------------|
| Action | Add new dependencies to existing backend environment |
| Dependencies | `openai-agents`, `mcp` |
| Method | Use `uv add` or `pip install` in existing venv |
| Gate | `import openai_agents` and `import mcp` succeed |

### Step 1.3: Configure Environment Variables

| Item | Description |
|------|-------------|
| Action | Add Phase III environment variables to `.env` |
| Variables | `OPENAI_API_KEY` |
| Gate | Environment variable accessible in application |

### Step 1.4: Create Phase III Module Structure

| Item | Description |
|------|-------------|
| Action | Create subdirectories for new components |
| Structure | `backend/mcp/`, `backend/agent/`, `backend/chat/` |
| Gate | Directories exist and are importable as Python modules |

---

## Phase 2: Database & ORM Setup

**Objective**: Extend the database schema with Conversation and Message tables while preserving the existing Task table.

**Prerequisites**: Phase 1 complete

**Verification**: New tables created, relationships enforced, existing data preserved

### Step 2.1: Define Conversation Model

| Item | Description |
|------|-------------|
| Action | Create SQLModel class for Conversation entity |
| File | `backend/models.py` (extend existing) |
| Fields | `id`, `user_id`, `created_at`, `updated_at` |
| Indexes | `user_id`, `(user_id, updated_at)` |
| Gate | Model imports without error |

### Step 2.2: Define Message Model

| Item | Description |
|------|-------------|
| Action | Create SQLModel class for Message entity |
| File | `backend/models.py` (extend existing) |
| Fields | `id`, `conversation_id`, `user_id`, `role`, `content`, `created_at` |
| Foreign Key | `conversation_id` → `conversation.id` (CASCADE) |
| Indexes | `conversation_id`, `(conversation_id, created_at)`, `user_id` |
| Gate | Model imports without error |

### Step 2.3: Define MessageRole Enum

| Item | Description |
|------|-------------|
| Action | Create enum for message roles |
| File | `backend/models.py` |
| Values | `user`, `assistant` |
| Gate | Enum usable in Message model |

### Step 2.4: Add Model Relationships

| Item | Description |
|------|-------------|
| Action | Define SQLModel relationships between Conversation and Message |
| Relationship | Conversation.messages ↔ Message.conversation |
| Gate | Relationship navigation works correctly |

### Step 2.5: Run Database Migration

| Item | Description |
|------|-------------|
| Action | Execute `SQLModel.metadata.create_all()` to create new tables |
| Method | Add to database initialization or run migration script |
| Preserve | Existing `task` table must not be modified |
| Gate | Tables `conversation` and `message` exist in database |

### Step 2.6: Verify Schema

| Item | Description |
|------|-------------|
| Action | Query database to confirm schema correctness |
| Checks | Tables exist, columns correct, indexes present, foreign keys work |
| Gate | All schema elements match specification |

---

## Phase 3: MCP Server Design

**Objective**: Implement the MCP Server exposing five task management tools that operate statelessly against the database.

**Prerequisites**: Phase 2 complete (database models exist)

**Verification**: All five tools registered, return correct responses, enforce user isolation

### Step 3.1: Initialize MCP Server Module

| Item | Description |
|------|-------------|
| Action | Create MCP server initialization |
| File | `backend/mcp/server.py` |
| Server Name | `todo-mcp-server` |
| Gate | Server instance can be created |

### Step 3.2: Implement add_task Tool

| Item | Description |
|------|-------------|
| Action | Create MCP tool for task creation |
| File | `backend/mcp/tools.py` |
| Inputs | `user_id` (required), `title` (required), `description` (optional) |
| Output | `{ status, task_id, title, message }` |
| Validation | Title required, max 200 chars; Description max 2000 chars |
| Database | INSERT into task table |
| Gate | Tool creates task and returns correct response |

### Step 3.3: Implement list_tasks Tool

| Item | Description |
|------|-------------|
| Action | Create MCP tool for task listing |
| File | `backend/mcp/tools.py` |
| Inputs | `user_id` (required), `status` (optional: all/pending/completed) |
| Output | `{ status, count, tasks[] }` |
| Filtering | By completion status when specified |
| Ordering | `created_at` descending |
| Gate | Tool returns filtered task list correctly |

### Step 3.4: Implement complete_task Tool

| Item | Description |
|------|-------------|
| Action | Create MCP tool for task completion |
| File | `backend/mcp/tools.py` |
| Inputs | `user_id` (required), `task_id` (required) |
| Output | `{ status, task_id, title, completed, message }` |
| Validation | Task must exist and belong to user |
| Database | UPDATE task SET completed = true |
| Gate | Tool marks task complete and returns confirmation |

### Step 3.5: Implement delete_task Tool

| Item | Description |
|------|-------------|
| Action | Create MCP tool for task deletion |
| File | `backend/mcp/tools.py` |
| Inputs | `user_id` (required), `task_id` (required) |
| Output | `{ status, task_id, title, message }` |
| Validation | Task must exist and belong to user |
| Database | DELETE from task table |
| Gate | Tool deletes task and returns confirmation |

### Step 3.6: Implement update_task Tool

| Item | Description |
|------|-------------|
| Action | Create MCP tool for task updates |
| File | `backend/mcp/tools.py` |
| Inputs | `user_id` (required), `task_id` (required), `title` (optional), `description` (optional) |
| Output | `{ status, task_id, title, description, message }` |
| Validation | At least one field required; field length limits |
| Database | UPDATE task with provided fields |
| Gate | Tool updates task and returns confirmation |

### Step 3.7: Register Tools with MCP Server

| Item | Description |
|------|-------------|
| Action | Register all five tools with the MCP server |
| Method | Use MCP SDK registration mechanism |
| Metadata | Include tool descriptions for agent |
| Gate | All tools discoverable via MCP protocol |

### Step 3.8: Enforce User Isolation

| Item | Description |
|------|-------------|
| Action | Verify all tools include user_id in database queries |
| Pattern | `WHERE user_id = :user_id` in all queries |
| Security | Return "Task not found" for unauthorized access |
| Gate | Cross-user access returns not found error |

---

## Phase 4: AI Agent Design

**Objective**: Configure the OpenAI Agent with the system prompt and MCP tool registration for natural language task management.

**Prerequisites**: Phase 3 complete (MCP tools available)

**Verification**: Agent interprets intent correctly, calls appropriate tools, confirms actions

### Step 4.1: Create Agent Module

| Item | Description |
|------|-------------|
| Action | Initialize OpenAI Agent configuration |
| File | `backend/agent/config.py` |
| SDK | OpenAI Agents SDK |
| Gate | Agent module importable |

### Step 4.2: Define System Prompt

| Item | Description |
|------|-------------|
| Action | Create the agent system prompt |
| File | `backend/agent/prompts.py` |
| Content | Capabilities, rules, examples, constraints per spec |
| Gate | Prompt stored as constant string |

### Step 4.3: Configure Agent Parameters

| Item | Description |
|------|-------------|
| Action | Set agent configuration parameters |
| Parameters | Model (gpt-4o), Temperature (0.7), Max Tokens (1000) |
| Gate | Agent uses correct parameters |

### Step 4.4: Register MCP Tools with Agent

| Item | Description |
|------|-------------|
| Action | Connect MCP tools to agent's tool registry |
| Method | Use OpenAI Agents SDK tool registration |
| Tools | add_task, list_tasks, complete_task, delete_task, update_task |
| Gate | Agent can discover and call all tools |

### Step 4.5: Implement Agent Runner

| Item | Description |
|------|-------------|
| Action | Create function to execute agent with message history |
| File | `backend/agent/runner.py` |
| Input | User message, conversation history, user_id |
| Output | Agent response, tool calls executed |
| Gate | Agent produces response for test input |

### Step 4.6: Configure Tool Call Handling

| Item | Description |
|------|-------------|
| Action | Implement tool call execution flow |
| Flow | Agent requests tool → Execute tool → Return result to agent |
| Injection | user_id injected into all tool calls |
| Gate | Tool calls execute and results returned to agent |

### Step 4.7: Verify Agent Constraints

| Item | Description |
|------|-------------|
| Action | Confirm agent never accesses database directly |
| Constraint | All data operations via MCP tools only |
| Gate | No direct database imports in agent module |

---

## Phase 5: Chat API Implementation

**Objective**: Create the FastAPI endpoint that orchestrates the chat flow from user message to agent response.

**Prerequisites**: Phase 3 and Phase 4 complete

**Verification**: Endpoint accepts messages, returns agent responses with tool call details

### Step 5.1: Create Chat Router

| Item | Description |
|------|-------------|
| Action | Create FastAPI router for chat endpoints |
| File | `backend/chat/router.py` |
| Prefix | `/api/{user_id}` |
| Gate | Router importable and can be included in app |

### Step 5.2: Define Request Schema

| Item | Description |
|------|-------------|
| Action | Create Pydantic model for chat request |
| File | `backend/chat/schemas.py` |
| Fields | `message` (required, max 2000), `conversation_id` (optional) |
| Gate | Schema validates correctly |

### Step 5.3: Define Response Schema

| Item | Description |
|------|-------------|
| Action | Create Pydantic model for chat response |
| File | `backend/chat/schemas.py` |
| Fields | `conversation_id`, `response`, `tool_calls[]` |
| Gate | Schema serializes correctly |

### Step 5.4: Implement Chat Endpoint

| Item | Description |
|------|-------------|
| Action | Create POST /api/{user_id}/chat endpoint |
| File | `backend/chat/router.py` |
| Flow | Validate → Load history → Store user message → Run agent → Store response → Return |
| Gate | Endpoint responds to requests |

### Step 5.5: Implement Conversation Loading

| Item | Description |
|------|-------------|
| Action | Create function to load conversation history from database |
| File | `backend/chat/services.py` |
| Query | SELECT messages WHERE conversation_id ORDER BY created_at |
| Limit | Most recent 100 messages |
| Gate | Messages loaded in correct order |

### Step 5.6: Implement Conversation Creation

| Item | Description |
|------|-------------|
| Action | Create function to create new conversation |
| File | `backend/chat/services.py` |
| Trigger | When conversation_id not provided |
| Gate | New conversation created and ID returned |

### Step 5.7: Integrate Agent Execution

| Item | Description |
|------|-------------|
| Action | Connect chat endpoint to agent runner |
| Flow | Pass message history → Execute agent → Capture response and tool calls |
| Gate | Agent executes and response captured |

### Step 5.8: Register Chat Router

| Item | Description |
|------|-------------|
| Action | Include chat router in FastAPI application |
| File | `backend/main.py` |
| Gate | Chat endpoint accessible via HTTP |

---

## Phase 6: Conversation Persistence

**Objective**: Ensure all messages are persisted to the database before and after agent execution for complete audit trail and stateless operation.

**Prerequisites**: Phase 5 complete

**Verification**: Messages persist, conversations survive restart, no in-memory state

### Step 6.1: Implement User Message Storage

| Item | Description |
|------|-------------|
| Action | Create function to store user message in database |
| File | `backend/chat/services.py` |
| Timing | Before agent execution |
| Fields | conversation_id, user_id, role=user, content, created_at |
| Gate | User message persists to database |

### Step 6.2: Implement Assistant Message Storage

| Item | Description |
|------|-------------|
| Action | Create function to store assistant response in database |
| File | `backend/chat/services.py` |
| Timing | After agent execution completes |
| Fields | conversation_id, user_id, role=assistant, content, created_at |
| Gate | Assistant message persists to database |

### Step 6.3: Update Conversation Timestamp

| Item | Description |
|------|-------------|
| Action | Update conversation.updated_at after each message |
| Trigger | After storing user or assistant message |
| Gate | updated_at reflects last message time |

### Step 6.4: Implement Tool Call Logging (Optional)

| Item | Description |
|------|-------------|
| Action | Store tool call metadata for debugging |
| Storage | Include in response or separate audit table |
| Gate | Tool calls visible in response |

### Step 6.5: Verify Stateless Operation

| Item | Description |
|------|-------------|
| Action | Confirm no conversation state in memory between requests |
| Check | No module-level variables storing conversation data |
| Check | Each request loads fresh from database |
| Gate | Server restart does not affect conversation continuity |

### Step 6.6: Implement Conversation List Endpoint

| Item | Description |
|------|-------------|
| Action | Create GET /api/{user_id}/conversations endpoint |
| File | `backend/chat/router.py` |
| Response | List of conversations with preview and timestamps |
| Gate | Endpoint returns user's conversations |

### Step 6.7: Implement Conversation Detail Endpoint

| Item | Description |
|------|-------------|
| Action | Create GET /api/{user_id}/conversations/{id} endpoint |
| File | `backend/chat/router.py` |
| Response | Full conversation with all messages |
| Gate | Endpoint returns conversation with messages |

### Step 6.8: Implement Conversation Delete Endpoint

| Item | Description |
|------|-------------|
| Action | Create DELETE /api/{user_id}/conversations/{id} endpoint |
| File | `backend/chat/router.py` |
| Behavior | Cascade delete conversation and all messages |
| Gate | Deletion removes conversation and messages |

---

## Phase 7: Frontend Integration

**Objective**: Set up the ChatKit UI to communicate with the backend chat API.

**Prerequisites**: Phase 5 and Phase 6 complete

**Verification**: UI sends messages, displays responses, shows conversation history

### Step 7.1: Evaluate ChatKit Options

| Item | Description |
|------|-------------|
| Action | Determine ChatKit integration approach |
| Options | Hosted ChatKit embed OR custom chat UI component |
| Decision | Based on domain requirements and authentication needs |
| Gate | Integration approach selected |

### Step 7.2: Create Chat Page

| Item | Description |
|------|-------------|
| Action | Create Next.js page for chat interface |
| File | `frontend/app/chat/page.tsx` |
| Components | Message list, input field, send button |
| Gate | Page renders correctly |

### Step 7.3: Implement Chat API Client

| Item | Description |
|------|-------------|
| Action | Create API client function for chat endpoint |
| File | `frontend/lib/api.ts` (extend existing) |
| Function | sendChatMessage(userId, message, conversationId?) |
| Gate | Function makes correct API call |

### Step 7.4: Implement Message Display

| Item | Description |
|------|-------------|
| Action | Create component to display chat messages |
| File | `frontend/components/chat-messages.tsx` |
| Features | User/assistant styling, timestamps, loading states |
| Gate | Messages display correctly |

### Step 7.5: Implement Message Input

| Item | Description |
|------|-------------|
| Action | Create component for message input |
| File | `frontend/components/chat-input.tsx` |
| Features | Text input, send button, enter key submit |
| Validation | Max 2000 characters |
| Gate | Input accepts and submits messages |

### Step 7.6: Implement Conversation State

| Item | Description |
|------|-------------|
| Action | Manage conversation state in React |
| State | Current conversation_id, message list, loading state |
| Flow | Send message → Show loading → Display response |
| Gate | State updates correctly on send/receive |

### Step 7.7: Load Existing Conversations

| Item | Description |
|------|-------------|
| Action | Implement conversation list and selection |
| Feature | Show user's conversations, allow switching |
| API | GET /api/{user_id}/conversations |
| Gate | User can view and switch conversations |

### Step 7.8: Handle Error States

| Item | Description |
|------|-------------|
| Action | Display user-friendly error messages |
| Errors | Network errors, auth errors, validation errors |
| Gate | Errors display clearly to user |

---

## Phase 8: Authentication Integration

**Objective**: Ensure chat endpoints are protected with JWT authentication and enforce user isolation.

**Prerequisites**: Phase II authentication working

**Verification**: Unauthenticated requests rejected, user_id extracted from JWT, cross-user access blocked

### Step 8.1: Verify Existing Auth Middleware

| Item | Description |
|------|-------------|
| Action | Confirm Phase II JWT middleware still operational |
| File | `backend/auth.py` |
| Gate | Middleware validates JWT tokens |

### Step 8.2: Apply Auth to Chat Endpoints

| Item | Description |
|------|-------------|
| Action | Add JWT dependency to all chat endpoints |
| Method | Use FastAPI Depends() with existing auth |
| Gate | Unauthenticated requests return 401 |

### Step 8.3: Extract user_id from JWT

| Item | Description |
|------|-------------|
| Action | Extract user_id from JWT token claims |
| Source | JWT `sub` claim |
| Injection | Pass to agent runner and MCP tools |
| Gate | user_id correctly extracted |

### Step 8.4: Validate URL user_id Matches JWT

| Item | Description |
|------|-------------|
| Action | Verify URL parameter {user_id} matches JWT user_id |
| Response | 403 Forbidden if mismatch |
| Gate | Cross-user access returns 403 |

### Step 8.5: Pass user_id to MCP Tools

| Item | Description |
|------|-------------|
| Action | Ensure authenticated user_id flows to all tool calls |
| Flow | Endpoint → Agent → Tool call → Database query |
| Gate | Tools always receive authenticated user_id |

### Step 8.6: Verify Conversation Ownership

| Item | Description |
|------|-------------|
| Action | Check conversation belongs to authenticated user |
| Check | On load, on message add |
| Response | 404 if conversation not found or unauthorized |
| Gate | Users cannot access other users' conversations |

### Step 8.7: Frontend Auth Token Attachment

| Item | Description |
|------|-------------|
| Action | Ensure frontend attaches JWT to chat requests |
| Header | Authorization: Bearer <token> |
| Gate | Requests include valid token |

---

## Phase 9: Error Handling & Validation

**Objective**: Implement comprehensive error handling for all failure modes with user-friendly messages.

**Prerequisites**: Phases 5-8 complete

**Verification**: All error cases handled gracefully, no stack traces exposed

### Step 9.1: Input Validation

| Item | Description |
|------|-------------|
| Action | Validate all API inputs |
| Checks | Message required, max 2000 chars; conversation_id format |
| Response | 400 with validation error details |
| Gate | Invalid input returns clear error |

### Step 9.2: Task Not Found Handling

| Item | Description |
|------|-------------|
| Action | Handle task not found in MCP tools |
| Response | `{ status: "error", error: "Task not found" }` |
| Agent | Translate to friendly message |
| Gate | Agent responds helpfully when task not found |

### Step 9.3: Empty Task List Handling

| Item | Description |
|------|-------------|
| Action | Handle no tasks scenario |
| Response | Empty array with helpful message |
| Agent | Suggest adding a task |
| Gate | Agent guides user when no tasks exist |

### Step 9.4: Invalid Task ID Handling

| Item | Description |
|------|-------------|
| Action | Handle invalid task ID format |
| Response | `{ status: "error", error: "Invalid task ID" }` |
| Gate | Clear error for non-integer task IDs |

### Step 9.5: Ambiguous Intent Handling

| Item | Description |
|------|-------------|
| Action | Agent asks for clarification when intent unclear |
| Behavior | Present options, ask user to specify |
| Gate | Agent doesn't guess on ambiguous input |

### Step 9.6: OpenAI API Error Handling

| Item | Description |
|------|-------------|
| Action | Handle OpenAI API failures gracefully |
| Errors | Rate limits, timeouts, service unavailable |
| Response | User-friendly message without technical details |
| Gate | API errors don't crash server |

### Step 9.7: Database Error Handling

| Item | Description |
|------|-------------|
| Action | Handle database connection/query errors |
| Response | Generic error message, log details server-side |
| Gate | Database errors don't expose internals |

### Step 9.8: MCP Tool Error Handling

| Item | Description |
|------|-------------|
| Action | Catch and handle MCP tool execution errors |
| Flow | Tool error → Agent receives error → Agent reports to user |
| Gate | Tool errors result in helpful user messages |

---

## Phase 10: Testing & Verification

**Objective**: Verify all functionality works correctly through systematic testing.

**Prerequisites**: Phases 1-9 complete

**Verification**: All test cases pass, system meets acceptance criteria

### Step 10.1: Test Task Creation Commands

| Item | Description |
|------|-------------|
| Commands | "Add a task to buy groceries", "I need to call mom", etc. |
| Verify | Task created in database, confirmation returned |
| Gate | All creation patterns work |

### Step 10.2: Test Task Listing Commands

| Item | Description |
|------|-------------|
| Commands | "Show me all my tasks", "What's pending?", etc. |
| Verify | Correct tasks returned, proper filtering |
| Gate | All listing patterns work |

### Step 10.3: Test Task Completion Commands

| Item | Description |
|------|-------------|
| Commands | "Mark task 3 as complete", "I finished the groceries task" |
| Verify | Task marked complete, confirmation returned |
| Gate | All completion patterns work |

### Step 10.4: Test Task Deletion Commands

| Item | Description |
|------|-------------|
| Commands | "Delete task 5", "Remove the meeting task" |
| Verify | Task deleted from database, confirmation returned |
| Gate | All deletion patterns work |

### Step 10.5: Test Task Update Commands

| Item | Description |
|------|-------------|
| Commands | "Change task 1 to call mom tonight", "Update description" |
| Verify | Task updated, changes persisted |
| Gate | All update patterns work |

### Step 10.6: Test Conversation Continuity

| Item | Description |
|------|-------------|
| Test | Send message → Get response → Send follow-up |
| Verify | Context maintained across messages |
| Gate | Follow-up messages understand context |

### Step 10.7: Test Stateless Behavior

| Item | Description |
|------|-------------|
| Test | Send message → Restart server → Send follow-up |
| Verify | Conversation continues seamlessly |
| Gate | Server restart doesn't break conversation |

### Step 10.8: Test Tool Chaining

| Item | Description |
|------|-------------|
| Test | "Complete the groceries task" (requires list then complete) |
| Verify | Agent chains tools correctly |
| Gate | Multi-tool operations work |

### Step 10.9: Test User Isolation

| Item | Description |
|------|-------------|
| Test | Create tasks as User A, query as User B |
| Verify | User B cannot see User A's tasks |
| Gate | Complete user isolation |

### Step 10.10: Test Error Scenarios

| Item | Description |
|------|-------------|
| Tests | Invalid task ID, task not found, empty list, etc. |
| Verify | Helpful error messages, no crashes |
| Gate | All error cases handled gracefully |

---

## Phase 11: Deployment Preparation

**Objective**: Prepare the system for production deployment.

**Prerequisites**: Phase 10 complete (all tests pass)

**Verification**: System deployable to production environment

### Step 11.1: Verify Environment Configuration

| Item | Description |
|------|-------------|
| Action | Confirm all environment variables documented |
| Variables | DATABASE_URL, BETTER_AUTH_SECRET, OPENAI_API_KEY |
| Gate | All required variables listed |

### Step 11.2: Configure Production Database

| Item | Description |
|------|-------------|
| Action | Verify Neon PostgreSQL connection works |
| Check | Connection string, SSL settings, connection pooling |
| Gate | Database accessible from deployment environment |

### Step 11.3: Configure CORS

| Item | Description |
|------|-------------|
| Action | Set CORS origins for production frontend |
| Settings | Allow frontend domain(s) |
| Gate | Frontend can communicate with backend |

### Step 11.4: Prepare Backend Deployment

| Item | Description |
|------|-------------|
| Action | Configure for deployment platform |
| Options | Railway, Render, Vercel Python, etc. |
| Gate | Backend deploys successfully |

### Step 11.5: Prepare Frontend Deployment

| Item | Description |
|------|-------------|
| Action | Configure Next.js for production |
| Platform | Vercel or alternative |
| Gate | Frontend deploys and connects to backend |

### Step 11.6: Verify Production Environment

| Item | Description |
|------|-------------|
| Action | Test complete flow in production |
| Test | Auth → Chat → Task operations → Persistence |
| Gate | Full functionality works in production |

---

## Phase 12: Documentation & Deliverables

**Objective**: Create comprehensive documentation for hackathon submission.

**Prerequisites**: All previous phases complete

**Verification**: Repository complete with all required documentation

### Step 12.1: Update README

| Item | Description |
|------|-------------|
| Action | Write comprehensive project README |
| Sections | Overview, architecture, setup, deployment, usage |
| Gate | README provides complete project context |

### Step 12.2: Document Architecture

| Item | Description |
|------|-------------|
| Action | Add architecture diagrams and explanations |
| Content | System diagram, data flow, component responsibilities |
| Gate | Architecture clearly explained |

### Step 12.3: Document API Endpoints

| Item | Description |
|------|-------------|
| Action | Ensure OpenAPI spec is complete |
| File | `specs/002-ai-todo-chatbot/contracts/chat-api.yaml` |
| Gate | All endpoints documented with examples |

### Step 12.4: Document Environment Setup

| Item | Description |
|------|-------------|
| Action | Write setup instructions |
| Content | Prerequisites, environment variables, install steps |
| Gate | New developer can set up project |

### Step 12.5: Document Natural Language Commands

| Item | Description |
|------|-------------|
| Action | List supported natural language patterns |
| Content | Examples for each operation type |
| Gate | Users know what commands work |

### Step 12.6: Verify Repository Structure

| Item | Description |
|------|-------------|
| Action | Confirm all required files present |
| Structure | /frontend, /backend, /specs, README, .env.example |
| Gate | Repository meets hackathon requirements |

### Step 12.7: Create Demo Script

| Item | Description |
|------|-------------|
| Action | Write demo walkthrough for judges |
| Content | Step-by-step demonstration of features |
| Gate | Demo showcases all capabilities |

---

## Constitution Check

### Principle I: Spec-Driven Only
- [x] All implementation steps reference specification documents
- [x] No implementation without explicit specification

### Principle II: Agentic Dev Stack Enforcement
- [x] Plan follows spec → plan → tasks → implement sequence
- [x] Each step is atomic and executable by Claude Code

### Principle III: No Manual Coding
- [x] All steps designed for agent execution
- [x] No instructions for manual file editing

### Technology Constraints
- [x] Backend: Python FastAPI
- [x] ORM: SQLModel
- [x] Database: Neon PostgreSQL
- [x] AI: OpenAI Agents SDK
- [x] Tools: MCP SDK
- [x] Auth: Better Auth (frontend), JWT (backend)

---

## Success Criteria

The plan is complete and implementation is successful when:

- [ ] All todo actions possible via natural language
- [ ] Agent uses MCP tools correctly for all operations
- [ ] Server is fully stateless (restart-safe)
- [ ] Conversations persist correctly in database
- [ ] User isolation enforced at all levels
- [ ] System handles all specified natural language patterns
- [ ] Documentation complete for hackathon submission

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| OpenAI API rate limits | Implement retry logic with backoff |
| Agent misinterprets intent | Design prompts to ask for clarification |
| MCP tool errors | Use try/catch with graceful error messages |
| Conversation history too large | Limit to 100 most recent messages |
| Database connection issues | Use connection pooling, handle errors gracefully |

---

## Next Steps

After plan approval, execute `/sp.tasks` to generate atomic implementation tasks from this plan.
