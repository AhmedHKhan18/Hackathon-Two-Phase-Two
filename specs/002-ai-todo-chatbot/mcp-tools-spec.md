# MCP Tools Specification: Todo Chatbot

**Feature**: 002-ai-todo-chatbot
**Date**: 2026-01-15
**Phase**: Design

## Overview

This document specifies the MCP (Model Context Protocol) tools that expose todo operations to the AI agent. Each tool is stateless, performs database operations via SQLModel, and returns structured responses for agent interpretation.

---

## MCP Server Configuration

### Server Identity

```
Name: todo-mcp-server
Version: 1.0.0
Protocol: MCP SDK (stdio transport for embedded, HTTP for standalone)
```

### Tool Registration

The MCP server MUST register exactly five tools:

1. `add_task` - Create a new task
2. `list_tasks` - Retrieve tasks with optional filtering
3. `complete_task` - Mark a task as completed
4. `delete_task` - Remove a task permanently
5. `update_task` - Modify task details

---

## Tool Specifications

### 1. add_task

**Purpose**: Create a new task for the specified user

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "description": "The user ID who owns this task (required)"
    },
    "title": {
      "type": "string",
      "description": "Task title (required, max 200 characters)"
    },
    "description": {
      "type": "string",
      "description": "Task description (optional, max 2000 characters)"
    }
  },
  "required": ["user_id", "title"]
}
```

**Behavior**:
1. Validate `user_id` is not empty
2. Validate `title` is not empty and <= 200 characters
3. Validate `description` (if provided) is <= 2000 characters
4. Create new Task record with:
   - `user_id` from input
   - `title` from input
   - `description` from input (or null)
   - `completed` = false
   - `created_at` = current timestamp
   - `updated_at` = current timestamp
5. Save to database
6. Return created task details

**Success Response**:
```json
{
  "status": "success",
  "task_id": 123,
  "title": "buy groceries",
  "message": "Task created successfully"
}
```

**Error Responses**:
| Condition | Response |
|-----------|----------|
| Empty title | `{"status": "error", "error": "Title is required"}` |
| Title too long | `{"status": "error", "error": "Title must be 200 characters or less"}` |
| Description too long | `{"status": "error", "error": "Description must be 2000 characters or less"}` |
| Database error | `{"status": "error", "error": "Failed to create task"}` |

---

### 2. list_tasks

**Purpose**: Retrieve tasks for the specified user with optional filtering

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "description": "The user ID whose tasks to retrieve (required)"
    },
    "status": {
      "type": "string",
      "enum": ["all", "pending", "completed"],
      "description": "Filter by completion status (optional, defaults to 'all')"
    }
  },
  "required": ["user_id"]
}
```

**Behavior**:
1. Validate `user_id` is not empty
2. Query database for tasks where `user_id` matches
3. Apply status filter if provided:
   - `"pending"` → WHERE `completed` = false
   - `"completed"` → WHERE `completed` = true
   - `"all"` or not provided → no additional filter
4. Order by `created_at` descending (newest first)
5. Return array of task objects

**Success Response**:
```json
{
  "status": "success",
  "count": 2,
  "tasks": [
    {
      "task_id": 1,
      "title": "buy groceries",
      "description": "milk, bread, eggs",
      "completed": false,
      "created_at": "2026-01-15T10:00:00Z",
      "updated_at": "2026-01-15T10:00:00Z"
    },
    {
      "task_id": 2,
      "title": "finish report",
      "description": null,
      "completed": true,
      "created_at": "2026-01-14T09:00:00Z",
      "updated_at": "2026-01-15T08:00:00Z"
    }
  ]
}
```

**Empty Response** (when no tasks found):
```json
{
  "status": "success",
  "count": 0,
  "tasks": [],
  "message": "No tasks found"
}
```

**Error Responses**:
| Condition | Response |
|-----------|----------|
| Invalid status value | `{"status": "error", "error": "Invalid status filter. Use 'all', 'pending', or 'completed'"}` |
| Database error | `{"status": "error", "error": "Failed to retrieve tasks"}` |

---

### 3. complete_task

**Purpose**: Mark a specific task as completed

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "description": "The user ID who owns this task (required)"
    },
    "task_id": {
      "type": "integer",
      "description": "The ID of the task to complete (required)"
    }
  },
  "required": ["user_id", "task_id"]
}
```

**Behavior**:
1. Validate `user_id` is not empty
2. Validate `task_id` is a positive integer
3. Query for task where `id` = `task_id` AND `user_id` = `user_id`
4. If not found, return error
5. Set `completed` = true
6. Set `updated_at` = current timestamp
7. Save to database
8. Return updated task details

**Success Response**:
```json
{
  "status": "success",
  "task_id": 123,
  "title": "buy groceries",
  "completed": true,
  "message": "Task marked as complete"
}
```

**Error Responses**:
| Condition | Response |
|-----------|----------|
| Task not found | `{"status": "error", "error": "Task not found", "task_id": 123}` |
| Invalid task_id | `{"status": "error", "error": "Invalid task ID"}` |
| User mismatch | `{"status": "error", "error": "Task not found", "task_id": 123}` |
| Database error | `{"status": "error", "error": "Failed to complete task"}` |

**Note**: User mismatch returns "Task not found" to avoid leaking information about other users' tasks.

---

### 4. delete_task

**Purpose**: Permanently remove a task

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "description": "The user ID who owns this task (required)"
    },
    "task_id": {
      "type": "integer",
      "description": "The ID of the task to delete (required)"
    }
  },
  "required": ["user_id", "task_id"]
}
```

**Behavior**:
1. Validate `user_id` is not empty
2. Validate `task_id` is a positive integer
3. Query for task where `id` = `task_id` AND `user_id` = `user_id`
4. If not found, return error
5. Store title for response before deletion
6. Delete the task record
7. Return confirmation with deleted task info

**Success Response**:
```json
{
  "status": "success",
  "task_id": 123,
  "title": "buy groceries",
  "message": "Task deleted successfully"
}
```

**Error Responses**:
| Condition | Response |
|-----------|----------|
| Task not found | `{"status": "error", "error": "Task not found", "task_id": 123}` |
| Invalid task_id | `{"status": "error", "error": "Invalid task ID"}` |
| User mismatch | `{"status": "error", "error": "Task not found", "task_id": 123}` |
| Database error | `{"status": "error", "error": "Failed to delete task"}` |

---

### 5. update_task

**Purpose**: Modify task title and/or description

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "description": "The user ID who owns this task (required)"
    },
    "task_id": {
      "type": "integer",
      "description": "The ID of the task to update (required)"
    },
    "title": {
      "type": "string",
      "description": "New task title (optional, max 200 characters)"
    },
    "description": {
      "type": "string",
      "description": "New task description (optional, max 2000 characters)"
    }
  },
  "required": ["user_id", "task_id"]
}
```

**Behavior**:
1. Validate `user_id` is not empty
2. Validate `task_id` is a positive integer
3. Validate at least one of `title` or `description` is provided
4. Validate `title` (if provided) is <= 200 characters
5. Validate `description` (if provided) is <= 2000 characters
6. Query for task where `id` = `task_id` AND `user_id` = `user_id`
7. If not found, return error
8. Update provided fields only (partial update)
9. Set `updated_at` = current timestamp
10. Save to database
11. Return updated task details

**Success Response**:
```json
{
  "status": "success",
  "task_id": 123,
  "title": "call mom tonight",
  "description": "about birthday party",
  "message": "Task updated successfully"
}
```

**Error Responses**:
| Condition | Response |
|-----------|----------|
| Task not found | `{"status": "error", "error": "Task not found", "task_id": 123}` |
| No fields to update | `{"status": "error", "error": "No fields provided to update"}` |
| Title too long | `{"status": "error", "error": "Title must be 200 characters or less"}` |
| Description too long | `{"status": "error", "error": "Description must be 2000 characters or less"}` |
| User mismatch | `{"status": "error", "error": "Task not found", "task_id": 123}` |
| Database error | `{"status": "error", "error": "Failed to update task"}` |

---

## Data Access Patterns

### User Isolation

All MCP tools MUST enforce user isolation:

```sql
-- Every query MUST include user_id filter
SELECT * FROM task WHERE id = :task_id AND user_id = :user_id;
UPDATE task SET ... WHERE id = :task_id AND user_id = :user_id;
DELETE FROM task WHERE id = :task_id AND user_id = :user_id;
```

### Database Connection

MCP tools MUST:
1. Use SQLModel for all database operations
2. Use connection pooling via Neon serverless driver
3. Not hold connections between requests (stateless)
4. Handle connection errors gracefully

### Transaction Boundaries

Each tool call is a single transaction:
- Success: commit
- Error: rollback (automatic with context manager)

---

## Error Handling

### Error Response Format

All errors follow this structure:
```json
{
  "status": "error",
  "error": "Human-readable error message",
  "task_id": 123  // Optional, included when relevant
}
```

### Error Categories

| Category | HTTP Equivalent | Handling |
|----------|-----------------|----------|
| Validation Error | 400 | Return descriptive error |
| Not Found | 404 | Return "Task not found" |
| Authorization | 403 | Return "Task not found" (mask) |
| Internal Error | 500 | Return generic error, log details |

---

## MCP SDK Integration

### Tool Registration Example

```python
# Reference structure only - not implementation
from mcp.server import Server
from mcp.types import Tool

server = Server("todo-mcp-server")

@server.tool("add_task")
async def add_task(user_id: str, title: str, description: str = None) -> dict:
    # Implementation
    pass

@server.tool("list_tasks")
async def list_tasks(user_id: str, status: str = "all") -> dict:
    # Implementation
    pass

@server.tool("complete_task")
async def complete_task(user_id: str, task_id: int) -> dict:
    # Implementation
    pass

@server.tool("delete_task")
async def delete_task(user_id: str, task_id: int) -> dict:
    # Implementation
    pass

@server.tool("update_task")
async def update_task(user_id: str, task_id: int, title: str = None, description: str = None) -> dict:
    # Implementation
    pass
```

### Tool Metadata for Agent

Each tool MUST provide descriptions for the agent:

| Tool | Description for Agent |
|------|----------------------|
| add_task | "Create a new task with a title and optional description" |
| list_tasks | "Get all tasks or filter by pending/completed status" |
| complete_task | "Mark a specific task as completed" |
| delete_task | "Permanently remove a task" |
| update_task | "Change a task's title or description" |

---

## Security Considerations

### Input Validation

All tools MUST:
1. Validate all input parameters before processing
2. Sanitize string inputs (prevent SQL injection via parameterized queries)
3. Enforce length limits
4. Reject unexpected fields

### User ID Trust

The `user_id` parameter:
1. MUST be provided by the calling agent (extracted from JWT by the chat endpoint)
2. MUST NOT be trusted from any other source
3. MUST be included in every database query

### Information Disclosure

When a task is not found due to:
- Task doesn't exist
- Task belongs to another user

Return the same error message: "Task not found"

This prevents enumeration attacks that could reveal other users' task IDs.

---

## Performance Considerations

### Query Optimization

- `list_tasks`: Use indexed query on (user_id, completed)
- Single task operations: Use indexed query on (id, user_id)

### Response Size

- `list_tasks`: Returns all matching tasks (no pagination for Phase III)
- Future consideration: Add pagination for users with many tasks

### Connection Management

- Use async database drivers for non-blocking operations
- Use connection pooling (Neon serverless handles this)
- Release connections immediately after query
