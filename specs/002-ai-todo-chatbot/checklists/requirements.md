# Requirements Checklist: AI Todo Chatbot

**Feature**: 002-ai-todo-chatbot
**Date**: 2026-01-15
**Phase**: Specification

## Functional Requirements Verification

### Chat Interface

- [ ] **FR-001**: System provides `POST /api/{user_id}/chat` endpoint
- [ ] **FR-002**: Endpoint accepts JSON body with `message` (required) and `conversation_id` (optional)
- [ ] **FR-003**: New conversation created when `conversation_id` not provided
- [ ] **FR-004**: Full conversation history loaded when `conversation_id` provided
- [ ] **FR-005**: User message stored before processing
- [ ] **FR-006**: Assistant response stored after processing
- [ ] **FR-007**: Response includes `conversation_id`, `response`, and `tool_calls`

### Agent Behavior

- [ ] **FR-008**: Agent interprets natural language to select MCP tools
- [ ] **FR-009**: Agent uses `add_task` for creation requests
- [ ] **FR-010**: Agent uses `list_tasks` for query requests
- [ ] **FR-011**: Agent uses `complete_task` for completion requests
- [ ] **FR-012**: Agent uses `delete_task` for removal requests
- [ ] **FR-013**: Agent uses `update_task` for modification requests
- [ ] **FR-014**: Agent calls `list_tasks` first for ambiguous references
- [ ] **FR-015**: Agent confirms all actions in natural language
- [ ] **FR-016**: Agent handles errors gracefully

### MCP Tools

- [ ] **FR-017**: MCP Server exposes exactly five tools
- [ ] **FR-018**: All tools accept `user_id` as required parameter
- [ ] **FR-019**: All tools persist changes to database
- [ ] **FR-020**: All tools return structured responses
- [ ] **FR-021**: Tools enforce user isolation

### Stateless Architecture

- [ ] **FR-022**: No conversation state in memory
- [ ] **FR-023**: No session data in memory
- [ ] **FR-024**: All context from database
- [ ] **FR-025**: Server is restart-safe
- [ ] **FR-026**: Any instance handles any request

### Database

- [ ] **FR-027**: `Conversation` table exists
- [ ] **FR-028**: `Message` table exists
- [ ] **FR-029**: `Task` table preserved from Phase II
- [ ] **FR-030**: Foreign key Message → Conversation

### Security

- [ ] **FR-031**: JWT required for chat requests
- [ ] **FR-032**: user_id extracted from JWT
- [ ] **FR-033**: URL user_id matches JWT user_id
- [ ] **FR-034**: Agent never accesses DB directly
- [ ] **FR-035**: MCP tools enforce ownership

---

## User Story Acceptance Criteria

### Story 1: Basic Task Creation via Chat

- [ ] "Add a task to buy groceries" creates task
- [ ] "I need to remember to call mom tonight" creates task
- [ ] Task with title and description both populated
- [ ] Ambiguous messages prompt clarification

### Story 2: List and Query Tasks via Chat

- [ ] "Show me all my tasks" lists all tasks
- [ ] "What's pending?" lists only incomplete tasks
- [ ] "What have I completed?" lists only completed tasks
- [ ] Empty task list handled gracefully

### Story 3: Complete Tasks via Chat

- [ ] "Mark task 3 as complete" completes task
- [ ] "Complete the groceries task" finds and completes
- [ ] "I finished the report task" works
- [ ] Non-existent task returns helpful error

### Story 4: Delete Tasks via Chat

- [ ] "Delete task 5" removes task
- [ ] "Delete the meeting task" finds and removes
- [ ] Vague reference prompts clarification
- [ ] Non-existent task returns helpful error

### Story 5: Update Tasks via Chat

- [ ] "Change task 1 to call mom tonight" updates title
- [ ] "Update the meeting task description" works
- [ ] Missing info prompts for clarification

### Story 6: Conversation Persistence

- [ ] Messages persist after page refresh
- [ ] Context maintained across messages
- [ ] New conversation created automatically

---

## MCP Tool Verification

### add_task

- [ ] Accepts user_id, title, description (optional)
- [ ] Returns task_id, status, title
- [ ] Validates title length (max 200)
- [ ] Validates description length (max 2000)

### list_tasks

- [ ] Accepts user_id, status (optional)
- [ ] Returns array of task objects
- [ ] Filters by pending/completed correctly
- [ ] Returns empty array (not error) when no tasks

### complete_task

- [ ] Accepts user_id, task_id
- [ ] Returns task_id, status, title
- [ ] Returns error for non-existent task
- [ ] Enforces user ownership

### delete_task

- [ ] Accepts user_id, task_id
- [ ] Returns task_id, status, title (of deleted)
- [ ] Returns error for non-existent task
- [ ] Enforces user ownership

### update_task

- [ ] Accepts user_id, task_id, title (opt), description (opt)
- [ ] Returns task_id, status, title
- [ ] Requires at least one field to update
- [ ] Validates field lengths

---

## Natural Language Coverage

- [ ] "Add a task to buy groceries"
- [ ] "Show me all my tasks"
- [ ] "What's pending?"
- [ ] "Mark task 3 as complete"
- [ ] "Delete the meeting task"
- [ ] "Change task 1 to call mom tonight"
- [ ] "I need to remember to pay bills"
- [ ] "What have I completed?"

---

## Non-Functional Requirements

### Performance

- [ ] Chat response < 3 seconds p95
- [ ] Database query < 100ms p95
- [ ] Conversation load < 500ms for 100 messages

### Security

- [ ] JWT validation on every request
- [ ] User isolation enforced
- [ ] No information leakage between users
- [ ] Secrets in environment variables only

### Scalability

- [ ] Stateless architecture verified
- [ ] No sticky sessions required
- [ ] Horizontal scaling compatible

---

## Specification Completeness

- [x] Main specification (spec.md) complete
- [x] Agent behavior specification complete
- [x] MCP tools specification complete
- [x] API contract (OpenAPI) complete
- [x] Data model specification complete
- [x] Requirements checklist complete
