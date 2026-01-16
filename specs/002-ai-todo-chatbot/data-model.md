# Data Model: AI Todo Chatbot

**Feature**: 002-ai-todo-chatbot
**Date**: 2026-01-15
**Phase**: Design

## Overview

This document defines the data entities for Phase III of the Todo application. It introduces two new entities (Conversation and Message) while preserving the existing Task entity from Phase II.

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     Better Auth (Frontend)                              │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ User                                                              │  │
│  │ - id: string (primary key)                                       │  │
│  │ - email: string                                                   │  │
│  │ - name: string                                                    │  │
│  │ - (managed by Better Auth)                                       │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              │ JWT contains user.id as "sub"
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     Backend Database                                     │
│                                                                         │
│  ┌────────────────────┐                                                 │
│  │ Task (Phase II)    │                                                 │
│  │ - id: integer (PK) │                                                 │
│  │ - user_id: string  │◀─────────────────────────────────────┐         │
│  │ - title: string    │                                       │         │
│  │ - description: str?│                                       │         │
│  │ - completed: bool  │                                       │         │
│  │ - created_at: dt   │                                       │         │
│  │ - updated_at: dt   │                                       │         │
│  └────────────────────┘                                       │         │
│                                                               │         │
│  ┌────────────────────┐       ┌────────────────────┐         │         │
│  │ Conversation (NEW) │       │ Message (NEW)      │         │         │
│  │ - id: integer (PK) │◀──────│ - conversation_id  │         │         │
│  │ - user_id: string  │───────│ - id: integer (PK) │─────────┘         │
│  │ - created_at: dt   │  1:N  │ - user_id: string  │                   │
│  │ - updated_at: dt   │       │ - role: enum       │                   │
│  └────────────────────┘       │ - content: text    │                   │
│                               │ - created_at: dt   │                   │
│                               └────────────────────┘                   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Entities

### 1. Task (Existing - No Changes)

The Task entity from Phase II remains unchanged. It is accessed exclusively through MCP tools.

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

---

### 2. Conversation (NEW)

Represents a chat session between a user and the AI assistant.

**Table Name**: `conversation`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PRIMARY KEY, AUTO INCREMENT | Unique conversation identifier |
| user_id | String(255) | NOT NULL, INDEX | Owner's Better Auth user ID |
| created_at | DateTime | NOT NULL, DEFAULT NOW | Conversation start timestamp |
| updated_at | DateTime | NOT NULL, DEFAULT NOW, ON UPDATE NOW | Last message timestamp |

**Indexes**:
- PRIMARY: `id`
- INDEX: `user_id` (for listing user's conversations)
- INDEX: `(user_id, updated_at)` (for sorted conversation list)

**SQLModel Definition** (reference):

```python
class Conversation(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(max_length=255, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    messages: list["Message"] = Relationship(back_populates="conversation")
```

---

### 3. Message (NEW)

Represents a single message in a conversation (user or assistant).

**Table Name**: `message`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PRIMARY KEY, AUTO INCREMENT | Unique message identifier |
| conversation_id | Integer | NOT NULL, FOREIGN KEY | Parent conversation reference |
| user_id | String(255) | NOT NULL, INDEX | Owner's Better Auth user ID |
| role | Enum('user', 'assistant') | NOT NULL | Message sender role |
| content | Text | NOT NULL | Message content |
| created_at | DateTime | NOT NULL, DEFAULT NOW | Message timestamp |

**Indexes**:
- PRIMARY: `id`
- INDEX: `conversation_id` (for loading conversation messages)
- INDEX: `(conversation_id, created_at)` (for ordered message loading)
- INDEX: `user_id` (for user isolation queries)

**Foreign Key**:
- `conversation_id` → `conversation.id` (ON DELETE CASCADE)

**SQLModel Definition** (reference):

```python
from enum import Enum

class MessageRole(str, Enum):
    user = "user"
    assistant = "assistant"

class Message(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id", index=True)
    user_id: str = Field(max_length=255, index=True)
    role: MessageRole
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    conversation: Conversation = Relationship(back_populates="messages")
```

---

## Relationships

### Cardinality

| Relationship | Cardinality | Description |
|--------------|-------------|-------------|
| User : Task | 1 : N | One user owns many tasks |
| User : Conversation | 1 : N | One user owns many conversations |
| Conversation : Message | 1 : N | One conversation contains many messages |
| User : Message | 1 : N | One user sends many messages (via conversations) |

### Referential Integrity

| Parent | Child | On Delete |
|--------|-------|-----------|
| Conversation | Message | CASCADE |

When a conversation is deleted, all its messages are automatically deleted.

---

## Validation Rules

### Conversation Validation

| Field | Rule | Error Message |
|-------|------|---------------|
| user_id | Required | "User ID is required" |
| user_id | Must match JWT | "Access denied" (403) |

### Message Validation

| Field | Rule | Error Message |
|-------|------|---------------|
| conversation_id | Required | "Conversation ID is required" |
| conversation_id | Must exist | "Conversation not found" (404) |
| user_id | Required | "User ID is required" |
| user_id | Must match conversation owner | "Access denied" (403) |
| role | Must be 'user' or 'assistant' | "Invalid message role" |
| content | Required | "Message content is required" |
| content | Max 10000 chars | "Message too long" |

---

## Business Rules

### 1. Conversation Creation

- Automatically created when user sends first message without conversation_id
- `user_id` is set from JWT token
- `created_at` and `updated_at` set to current time

### 2. Message Creation

- `user_id` must match conversation owner
- `created_at` set to current time
- Conversation's `updated_at` updated to current time
- Messages are append-only (no updates or deletes of individual messages)

### 3. Conversation Loading

- Load all messages ordered by `created_at` ascending
- Limit to most recent 100 messages for agent context
- User can only load their own conversations

### 4. Conversation Deletion

- Deletes conversation and all messages (cascade)
- Only owner can delete their conversations
- Does NOT delete tasks (tasks are independent)

---

## State Diagrams

### Conversation Lifecycle

```
                              create_conversation()
                                      │
                                      ▼
                              ┌───────────────┐
                              │    ACTIVE     │
                              │               │◀──────────┐
                              │ messages: N   │           │
                              └───────────────┘           │
                                      │                   │
                add_message()         │                   │ add_message()
                (user or assistant)   │                   │
                                      └───────────────────┘
                                      │
                              delete_conversation()
                                      │
                                      ▼
                              ┌───────────────┐
                              │   DELETED     │
                              │ (hard delete) │
                              └───────────────┘
```

### Message Flow

```
                    ┌─────────────────────────────────────┐
                    │                                     │
                    ▼                                     │
            ┌───────────────┐                    ┌───────────────┐
            │  USER MESSAGE │───────────────────▶│ ASST MESSAGE  │
            │               │     agent          │               │
            │ role="user"   │     processing     │role="assistant│
            └───────────────┘                    └───────────────┘
                    ▲                                     │
                    │                                     │
                    └─────────────────────────────────────┘
                              next user input
```

---

## Request/Response Models

### ChatRequest (POST /api/{user_id}/chat)

```json
{
  "message": "string (required, max 2000)",
  "conversation_id": "integer (optional)"
}
```

### ChatResponse

```json
{
  "conversation_id": "integer",
  "response": "string",
  "tool_calls": [
    {
      "tool": "string",
      "arguments": {},
      "result": {}
    }
  ]
}
```

### ConversationResponse

```json
{
  "id": "integer",
  "user_id": "string",
  "messages": [
    {
      "id": "integer",
      "role": "user | assistant",
      "content": "string",
      "created_at": "ISO 8601 datetime"
    }
  ],
  "created_at": "ISO 8601 datetime",
  "updated_at": "ISO 8601 datetime"
}
```

---

## Database Schema SQL (Reference)

```sql
-- Existing Task table (unchanged from Phase II)
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

-- New Conversation table
CREATE TABLE conversation (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conversation_user_id ON conversation(user_id);
CREATE INDEX idx_conversation_user_updated ON conversation(user_id, updated_at);

-- New Message table
CREATE TYPE message_role AS ENUM ('user', 'assistant');

CREATE TABLE message (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversation(id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL,
    role message_role NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_message_conversation ON message(conversation_id);
CREATE INDEX idx_message_conversation_created ON message(conversation_id, created_at);
CREATE INDEX idx_message_user_id ON message(user_id);
```

**Note**: Schema is created by SQLModel.metadata.create_all() - this SQL is for reference only.

---

## Migration Strategy

### Phase III Migration

1. Run SQLModel's `create_all()` to create new tables
2. Existing `task` table is preserved (no changes)
3. New `conversation` and `message` tables are created
4. Idempotent: safe to run multiple times

### Rollback Procedure

If Phase III needs to be rolled back:
1. Drop `message` table first (foreign key constraint)
2. Drop `conversation` table
3. `task` table remains unchanged

```sql
-- Rollback SQL (if needed)
DROP TABLE IF EXISTS message;
DROP TABLE IF EXISTS conversation;
DROP TYPE IF EXISTS message_role;
```

---

## Data Retention

### Phase III Policy

| Entity | Retention | Notes |
|--------|-----------|-------|
| Task | Indefinite | User-managed lifecycle |
| Conversation | Indefinite | User can delete |
| Message | Tied to Conversation | Cascade delete |

### Future Considerations

- Auto-archive conversations older than 90 days
- Conversation export feature
- Message search/indexing
