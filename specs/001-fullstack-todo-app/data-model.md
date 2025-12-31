# Data Model: Full-Stack Todo Web Application

**Feature**: 001-fullstack-todo-app
**Date**: 2025-12-30
**Phase**: 1 - Design

## Overview

This document defines the data entities, their fields, relationships, and validation rules for the Phase II Todo application.

---

## Entities

### 1. Task

The primary entity representing a unit of work to be completed.

**Table Name**: `task`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PRIMARY KEY, AUTO INCREMENT | Unique task identifier |
| user_id | String(255) | NOT NULL, INDEX | Owner's Better Auth user ID |
| title | String(200) | NOT NULL | Task title (required) |
| description | String(2000) | NULLABLE | Task description (optional) |
| completed | Boolean | NOT NULL, DEFAULT FALSE | Completion status |
| created_at | DateTime | NOT NULL, DEFAULT NOW | Creation timestamp |
| updated_at | DateTime | NOT NULL, DEFAULT NOW, ON UPDATE NOW | Last modification timestamp |

**Indexes**:
- PRIMARY: `id`
- INDEX: `user_id` (for filtering tasks by user)
- INDEX: `(user_id, completed)` (for filtered list queries)

**SQLModel Definition** (reference):

```python
class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(max_length=255, index=True)
    title: str = Field(max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

---

### 2. User (External Reference)

Users are managed by Better Auth on the frontend. The backend does NOT store user records - it only references user IDs from JWT tokens.

**Source**: Better Auth managed tables (session, account, user)

**Referenced Field**: `user.id` (string, extracted from JWT `sub` claim)

**Notes**:
- No User table in backend database
- user_id is trusted from JWT token only
- No foreign key constraint (Better Auth manages users separately)

---

## Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                     Better Auth (Frontend)                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ User                                                  │  │
│  │ - id: string (primary key)                           │  │
│  │ - email: string                                       │  │
│  │ - name: string                                        │  │
│  │ - (managed by Better Auth)                           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ JWT contains user.id as "sub"
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Backend Database                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Task                                                  │  │
│  │ - id: integer (PK)                                   │  │
│  │ - user_id: string (references User.id via JWT)       │  │
│  │ - title: string                                       │  │
│  │ - description: string?                               │  │
│  │ - completed: boolean                                 │  │
│  │ - created_at: datetime                               │  │
│  │ - updated_at: datetime                               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

**Cardinality**:
- User : Task = 1 : N (one user owns many tasks)
- Task : User = N : 1 (each task belongs to exactly one user)

---

## Validation Rules

### Task Validation

| Field | Rule | Error Message |
|-------|------|---------------|
| title | Required | "Title is required" |
| title | Max 200 chars | "Title must be 200 characters or less" |
| description | Max 2000 chars | "Description must be 2000 characters or less" |
| completed | Boolean only | "Completed must be true or false" |
| user_id | Must match JWT | "Access denied" (403) |

### Business Rules

1. **Task Creation**:
   - user_id is set from JWT token, not from request body
   - completed defaults to false
   - created_at and updated_at set to current time

2. **Task Update**:
   - Only title, description, and completed can be updated
   - user_id cannot be changed
   - updated_at set to current time on any change

3. **Task Deletion**:
   - Soft delete not required (hard delete)
   - Only owner can delete their tasks

4. **Task Listing**:
   - Always filtered by authenticated user's ID
   - Returns empty list if no tasks (not 404)

---

## State Transitions

### Task Completion State

```
                    mark_complete()
    ┌─────────────────────────────────────────┐
    │                                         │
    ▼                                         │
┌──────────┐                           ┌──────────┐
│ PENDING  │ ─────────────────────────▶│ COMPLETE │
│(completed│     toggle_complete()     │(completed│
│ = false) │◀───────────────────────── │ = true)  │
└──────────┘                           └──────────┘
                mark_incomplete()
```

**State Rules**:
- New tasks start as PENDING (completed = false)
- Users can toggle between states at any time
- State persists across sessions

---

## Request/Response Models

### TaskCreate (POST request body)

```json
{
  "title": "string (required, max 200)",
  "description": "string (optional, max 2000)"
}
```

### TaskUpdate (PUT request body)

```json
{
  "title": "string (optional, max 200)",
  "description": "string (optional, max 2000)",
  "completed": "boolean (optional)"
}
```

### TaskResponse (Response body)

```json
{
  "id": "integer",
  "user_id": "string",
  "title": "string",
  "description": "string | null",
  "completed": "boolean",
  "created_at": "ISO 8601 datetime",
  "updated_at": "ISO 8601 datetime"
}
```

### TaskListResponse (GET /tasks response)

```json
[
  {
    "id": 1,
    "user_id": "user_abc123",
    "title": "Buy groceries",
    "description": "Milk, bread, eggs",
    "completed": false,
    "created_at": "2025-12-30T10:00:00Z",
    "updated_at": "2025-12-30T10:00:00Z"
  },
  ...
]
```

---

## Database Schema SQL (Reference)

```sql
CREATE TABLE task (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description VARCHAR(2000),
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_task_user_id ON task(user_id);
CREATE INDEX idx_task_user_completed ON task(user_id, completed);
```

**Note**: Schema is created by SQLModel.metadata.create_all() - this SQL is for reference only.

---

## Migration Strategy

### Phase II (Initial)
- No migration framework
- SQLModel creates tables on startup
- Idempotent (safe to run multiple times)
- Development database can be reset as needed

### Phase III (Future)
- Alembic migrations recommended
- Add migration for chatbot-related fields
- Preserve existing task data
