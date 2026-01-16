# Feature Specification: AI-Powered Todo Chatbot

**Feature Branch**: `002-ai-todo-chatbot`
**Created**: 2026-01-15
**Status**: Draft
**Phase**: Phase III - AI Chatbot Integration
**Spec Version**: 1.0

## Overview

This specification defines Phase III of the Todo application: an AI-powered chatbot that allows users to manage their todo tasks through natural language conversation. The chatbot uses the OpenAI Agents SDK for reasoning and MCP (Model Context Protocol) tools to expose todo operations.

The system is designed to be fully stateless and horizontally scalable. All conversation context is persisted in the database, and the MCP tools operate independently without server-side session storage.

## Scope

### In Scope

- Natural language task management via chatbot interface
- Conversation persistence in database
- MCP Server exposing task operations as tools
- OpenAI Agent integration for intent interpretation
- Stateless request handling (no in-memory sessions)
- All Basic Level Todo features:
  - Add task
  - List tasks
  - Update task
  - Complete task
  - Delete task

### Out of Scope

- Real-time chat (WebSocket streaming) - single request/response model
- Voice input/output
- Multi-language support (English only for Phase III)
- Advanced AI features (task prioritization, scheduling suggestions)
- Task sharing or collaboration
- Mobile-native applications
- Offline functionality
- Integration with external calendars/services

## System Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Frontend (ChatKit UI)                          │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  OpenAI ChatKit (Hosted)                                         │   │
│  │  - Sends user messages to POST /api/{user_id}/chat              │   │
│  │  - Displays assistant responses                                  │   │
│  │  - Maintains conversation thread visually                        │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP POST (JSON)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          Backend (FastAPI)                              │
│                                                                         │
│  ┌────────────────────┐    ┌────────────────────┐                      │
│  │   Chat Endpoint    │───▶│   OpenAI Agent     │                      │
│  │   /api/{user_id}/  │    │   (Agents SDK)     │                      │
│  │   chat             │◀───│                    │                      │
│  └────────────────────┘    └────────────────────┘                      │
│           │                         │                                   │
│           │                         │ Tool Calls                        │
│           ▼                         ▼                                   │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │                      MCP Server                                 │    │
│  │  ┌──────────┐ ┌───────────┐ ┌───────────────┐ ┌─────────────┐ │    │
│  │  │ add_task │ │list_tasks │ │ complete_task │ │ delete_task │ │    │
│  │  └──────────┘ └───────────┘ └───────────────┘ └─────────────┘ │    │
│  │  ┌─────────────┐                                               │    │
│  │  │ update_task │                                               │    │
│  │  └─────────────┘                                               │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                    │                                    │
└────────────────────────────────────│────────────────────────────────────┘
                                     │ SQLModel ORM
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Neon Serverless PostgreSQL                           │
│                                                                         │
│  ┌───────────────┐  ┌──────────────────┐  ┌─────────────────┐          │
│  │     Task      │  │   Conversation   │  │     Message     │          │
│  │   (existing)  │  │     (new)        │  │     (new)       │          │
│  └───────────────┘  └──────────────────┘  └─────────────────┘          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
1. User Input
   ├─▶ ChatKit UI receives user message
   └─▶ POST /api/{user_id}/chat with message + optional conversation_id

2. Server Processing (Stateless)
   ├─▶ Authenticate request (JWT validation)
   ├─▶ Load conversation history from DB (or create new conversation)
   ├─▶ Store incoming user message in DB
   ├─▶ Build message history for agent
   ├─▶ Execute OpenAI Agent with MCP tools
   ├─▶ Agent selects and calls appropriate MCP tool(s)
   ├─▶ MCP tools execute against database
   ├─▶ Agent formulates natural language response
   ├─▶ Store assistant response in DB
   └─▶ Return response to client

3. Response
   └─▶ ChatKit displays assistant response
```

### Stateless Guarantees

The following constraints MUST be enforced to ensure horizontal scalability:

1. **No in-memory session storage**: Every request is independent
2. **All state in database**: Conversations, messages, and tasks persist in PostgreSQL
3. **Request-scoped processing**: Each request loads, processes, and saves without retained state
4. **Restart-safe**: Server can restart between requests with zero data loss
5. **Load-balancer compatible**: Any server instance can handle any request

## User Scenarios & Testing

### User Story 1 - Basic Task Creation via Chat (Priority: P1)

As an authenticated user, I want to create tasks by typing natural language commands so that I can quickly add items to my todo list without navigating forms.

**Why this priority**: Task creation is the fundamental action. Without it, the chatbot provides no value. This demonstrates the core natural language to action pipeline.

**Independent Test**: Can be fully tested by sending messages like "Add a task to buy groceries" and verifying a task appears in the database. Delivers immediate value as a conversational task manager.

**Acceptance Scenarios**:

1. **Given** I am authenticated and in the chat interface, **When** I type "Add a task to buy groceries", **Then** a new task with title "buy groceries" is created and the assistant confirms the creation.
2. **Given** I am authenticated, **When** I type "I need to remember to call mom tonight", **Then** the assistant creates a task with an appropriate title and confirms.
3. **Given** I am authenticated, **When** I type "Add task: finish report with description needs charts and data", **Then** a task is created with both title and description populated.
4. **Given** I type an ambiguous message like "milk", **When** the assistant processes it, **Then** the assistant asks for clarification before creating a task.

---

### User Story 2 - List and Query Tasks via Chat (Priority: P2)

As an authenticated user, I want to ask about my tasks using natural language so that I can quickly review what I need to do.

**Why this priority**: After creating tasks, users need to retrieve them. This validates the agent can interpret queries and return formatted results.

**Independent Test**: Can be tested by creating tasks, then asking "Show me all my tasks" and verifying the response lists all tasks. Delivers task visibility through conversation.

**Acceptance Scenarios**:

1. **Given** I have existing tasks, **When** I type "Show me all my tasks", **Then** the assistant lists all my tasks with their titles and status.
2. **Given** I have completed and pending tasks, **When** I type "What's pending?", **Then** the assistant lists only incomplete tasks.
3. **Given** I have completed tasks, **When** I type "What have I completed?", **Then** the assistant lists only completed tasks.
4. **Given** I have no tasks, **When** I type "Show my tasks", **Then** the assistant responds with a message indicating no tasks exist.

---

### User Story 3 - Complete Tasks via Chat (Priority: P3)

As an authenticated user, I want to mark tasks as complete using natural language so that I can track my progress conversationally.

**Why this priority**: Completion tracking is essential for task management utility. This tests the agent's ability to identify and modify specific tasks.

**Independent Test**: Can be tested by creating a task, saying "Mark task 1 as complete", and verifying the task's completed status changes. Delivers progress tracking capability.

**Acceptance Scenarios**:

1. **Given** I have an incomplete task with ID 3, **When** I type "Mark task 3 as complete", **Then** the task is marked complete and the assistant confirms.
2. **Given** I have a task titled "buy groceries", **When** I type "Complete the groceries task", **Then** the assistant identifies the task, marks it complete, and confirms.
3. **Given** I have multiple tasks, **When** I type "I finished the report task", **Then** the assistant locates the matching task and marks it complete.
4. **Given** I reference a non-existent task, **When** I type "Complete task 999", **Then** the assistant responds that the task was not found.

---

### User Story 4 - Delete Tasks via Chat (Priority: P4)

As an authenticated user, I want to remove tasks using natural language so that I can keep my list clean.

**Why this priority**: Deletion completes the basic CRUD operations. Tests the agent's ability to perform destructive actions safely.

**Independent Test**: Can be tested by creating a task, saying "Delete the meeting task", and verifying removal. Delivers list maintenance capability.

**Acceptance Scenarios**:

1. **Given** I have a task with ID 5, **When** I type "Delete task 5", **Then** the task is permanently removed and the assistant confirms.
2. **Given** I have a task titled "meeting notes", **When** I type "Delete the meeting task", **Then** the assistant locates and removes the matching task.
3. **Given** a vague reference, **When** I type "Remove that thing about bills", **Then** the assistant either deletes the matching task or asks for clarification if ambiguous.
4. **Given** I reference a non-existent task, **When** I type "Delete task 999", **Then** the assistant responds that the task was not found.

---

### User Story 5 - Update Tasks via Chat (Priority: P5)

As an authenticated user, I want to modify task details using natural language so that I can keep my tasks accurate.

**Why this priority**: Updates allow users to refine tasks without delete/recreate. Tests nuanced agent understanding.

**Independent Test**: Can be tested by creating a task, saying "Change task 1 to call mom tonight", and verifying the title update. Delivers task refinement capability.

**Acceptance Scenarios**:

1. **Given** I have task ID 1 titled "call dad", **When** I type "Change task 1 to call mom tonight", **Then** the task title is updated and the assistant confirms.
2. **Given** I have a task titled "meeting", **When** I type "Update the meeting task description to discuss Q1 results", **Then** the description is updated.
3. **Given** I have a task, **When** I type "Rename task 2 to something better", **Then** the assistant asks for the new title.

---

### User Story 6 - Conversation Persistence (Priority: P6)

As an authenticated user, I want my chat history to persist across sessions so that I can continue conversations where I left off.

**Why this priority**: Persistence is critical for the stateless architecture claim. Validates database-backed conversation storage.

**Independent Test**: Can be tested by sending messages, refreshing the page, and verifying previous messages appear. Delivers conversation continuity.

**Acceptance Scenarios**:

1. **Given** I have an ongoing conversation, **When** I refresh the page and return to chat, **Then** my previous messages and assistant responses are displayed.
2. **Given** I send multiple messages in a conversation, **When** I send a follow-up like "also add milk", **Then** the assistant understands context from prior messages.
3. **Given** I have no prior conversation, **When** I send my first message, **Then** a new conversation is created automatically.

---

### Edge Cases

- **Ambiguous task references**: When user says "delete that task" but multiple tasks match, the agent should list options and ask for clarification
- **Empty task operations**: When user tries to complete/delete/update with no tasks existing, provide helpful guidance
- **Invalid task IDs**: When user provides a task ID that doesn't exist, respond gracefully
- **Very long messages**: System should handle messages up to 2000 characters without truncation issues
- **Rapid sequential messages**: System should handle back-to-back messages correctly (conversation ordering)
- **Tool errors**: When MCP tool fails, agent should report error gracefully without exposing internals
- **Session expiry mid-chat**: When JWT expires during conversation, return 401 and require re-authentication
- **Concurrent edits**: If user modifies tasks via both chat and direct API, both should reflect correctly (eventual consistency acceptable)

## Requirements

### Functional Requirements

**Chat Interface**

- **FR-001**: System MUST provide a single chat endpoint at `POST /api/{user_id}/chat`
- **FR-002**: System MUST accept a JSON body with `message` (required) and `conversation_id` (optional)
- **FR-003**: System MUST create a new conversation when `conversation_id` is not provided
- **FR-004**: System MUST load full conversation history when `conversation_id` is provided
- **FR-005**: System MUST store every user message in the database before processing
- **FR-006**: System MUST store every assistant response in the database after processing
- **FR-007**: System MUST return a JSON response with `conversation_id`, `response`, and `tool_calls`

**Agent Behavior**

- **FR-008**: Agent MUST interpret natural language intent to select appropriate MCP tools
- **FR-009**: Agent MUST use `add_task` tool for task creation requests
- **FR-010**: Agent MUST use `list_tasks` tool for task query requests
- **FR-011**: Agent MUST use `complete_task` tool for task completion requests
- **FR-012**: Agent MUST use `delete_task` tool for task removal requests
- **FR-013**: Agent MUST use `update_task` tool for task modification requests
- **FR-014**: Agent MUST call `list_tasks` first when task reference is ambiguous
- **FR-015**: Agent MUST confirm all actions in natural language
- **FR-016**: Agent MUST handle errors gracefully and report them in natural language

**MCP Tools**

- **FR-017**: MCP Server MUST expose exactly five tools: `add_task`, `list_tasks`, `complete_task`, `delete_task`, `update_task`
- **FR-018**: All MCP tools MUST accept `user_id` as a required parameter
- **FR-019**: All MCP tools MUST persist changes to the database
- **FR-020**: All MCP tools MUST return structured responses for agent interpretation
- **FR-021**: MCP tools MUST NOT access data belonging to other users

**Stateless Architecture**

- **FR-022**: Server MUST NOT store any conversation state in memory
- **FR-023**: Server MUST NOT store any session data in memory
- **FR-024**: All conversation context MUST be loaded from and saved to the database
- **FR-025**: Server MUST be restart-safe with zero data loss
- **FR-026**: Any server instance MUST be able to handle any user's request

**Database**

- **FR-027**: System MUST add `Conversation` table for tracking conversations
- **FR-028**: System MUST add `Message` table for storing chat messages
- **FR-029**: System MUST preserve existing `Task` table schema from Phase II
- **FR-030**: System MUST support foreign key relationship between Message and Conversation

**Security**

- **FR-031**: System MUST require valid JWT tokens for all chat requests
- **FR-032**: System MUST extract user_id from JWT token, not request body
- **FR-033**: System MUST validate that user_id in URL matches JWT user_id
- **FR-034**: Agent MUST NEVER access database directly - only via MCP tools
- **FR-035**: MCP tools MUST enforce user ownership for all operations

### Key Entities

- **Conversation**: Represents a chat session between a user and the assistant. Contains: unique ID, owner user_id, creation timestamp, update timestamp. A user can have multiple conversations.

- **Message**: Represents a single chat message. Contains: unique ID, conversation reference, role (user/assistant), content text, creation timestamp. Each message belongs to exactly one conversation.

- **Task**: (Existing from Phase II) Represents a unit of work. Contains: ID, user_id, title, description, completed status, timestamps. Accessed exclusively via MCP tools.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can create tasks via natural language in under 5 seconds end-to-end
- **SC-002**: Agent correctly interprets intent for basic CRUD operations 95%+ of the time
- **SC-003**: Chat responses return within 3 seconds for typical messages
- **SC-004**: Conversation history loads within 1 second for conversations with up to 100 messages
- **SC-005**: 100% of tool operations persist correctly to database
- **SC-006**: Zero data leakage between users (strict user isolation)
- **SC-007**: Server can be restarted without losing any conversation data
- **SC-008**: System handles 20 concurrent chat sessions without degradation
- **SC-009**: Agent provides helpful error messages for invalid operations
- **SC-010**: All specified natural language patterns are correctly interpreted

## Assumptions

- Users are authenticated via Better Auth JWT tokens (same as Phase II)
- Users have modern browsers supporting ChatKit embedded interface
- Internet connectivity is stable (offline not supported)
- English language only for Phase III
- Maximum message length: 2000 characters
- Maximum conversation history: 100 messages loaded per request
- OpenAI API is available and responsive
- MCP SDK supports required tool patterns
- Database supports concurrent writes from multiple MCP tool calls

## Dependencies

- Phase II backend (FastAPI, SQLModel, JWT auth) must be operational
- OpenAI Agents SDK must be installed and configured
- MCP SDK must be installed and configured
- OpenAI API key must be configured in environment
- ChatKit UI must be deployable and connectable
- Neon PostgreSQL must support additional tables

## Risks

- **Risk**: OpenAI API rate limits could impact user experience during high usage
  - **Mitigation**: Implement request queuing and user feedback for delays

- **Risk**: Agent may misinterpret ambiguous natural language inputs
  - **Mitigation**: Design agent prompts to ask for clarification when uncertain

- **Risk**: MCP tool errors could leave data in inconsistent state
  - **Mitigation**: Use database transactions for multi-step operations

- **Risk**: Conversation history growth could impact performance
  - **Mitigation**: Limit loaded history to most recent 100 messages; implement pagination for older messages

- **Risk**: Complex tool chains (list then delete) could fail mid-execution
  - **Mitigation**: Agent should verify each step and report partial completions

## Non-Functional Requirements

### Performance

- Chat endpoint response time: < 3 seconds p95
- Database query time: < 100ms p95
- Conversation load time: < 500ms for 100 messages
- Memory usage: No conversation state retained between requests

### Reliability

- Availability target: 99.9% uptime
- Data durability: All messages persisted before acknowledgment
- Error recovery: Graceful degradation when OpenAI API unavailable

### Security

- Authentication: JWT token validation on every request
- Authorization: User can only access their own conversations and tasks
- Data isolation: MCP tools enforce user_id filtering
- Secrets: API keys stored in environment variables only

### Scalability

- Horizontal scaling: Stateless architecture supports N server instances
- Database scaling: Neon Serverless handles connection pooling
- No sticky sessions required
