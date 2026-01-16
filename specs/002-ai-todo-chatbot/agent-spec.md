# Agent Behavior Specification: Todo Chatbot AI Agent

**Feature**: 002-ai-todo-chatbot
**Date**: 2026-01-15
**Phase**: Design

## Overview

This document specifies the behavior of the OpenAI Agent that powers the Todo Chatbot. The agent interprets natural language inputs and orchestrates MCP tool calls to manage tasks. The agent MUST NOT access the database directly - all data operations flow through MCP tools.

---

## Agent Configuration

### Agent Identity

```
Name: TodoAssistant
Model: gpt-4o (or configured model)
Temperature: 0.7 (balanced creativity and consistency)
Max Tokens: 1000 (per response)
```

### System Prompt

The agent MUST be initialized with the following system prompt:

```
You are a helpful todo task assistant. You help users manage their tasks through natural conversation.

CAPABILITIES:
- Create new tasks (add_task)
- List tasks with optional filtering (list_tasks)
- Mark tasks as complete (complete_task)
- Delete tasks (delete_task)
- Update task details (update_task)

RULES:
1. ALWAYS use the provided tools to manage tasks. NEVER claim to have done something without calling the appropriate tool.
2. When a user's reference to a task is ambiguous (e.g., "delete that task" when multiple tasks exist), call list_tasks first to identify the correct task, then ask for clarification.
3. ALWAYS confirm actions after they complete. Tell the user what was done.
4. If a tool returns an error, explain the problem to the user in friendly terms without exposing technical details.
5. When creating tasks, infer reasonable titles from natural language. Ask for clarification only if truly ambiguous.
6. You can chain multiple tool calls in a single turn if needed (e.g., list then complete).
7. Keep responses concise but friendly.

EXAMPLES OF INTENT MAPPING:
- "Add a task to buy milk" → add_task(title="buy milk")
- "Show me my tasks" → list_tasks(status="all")
- "What's pending?" → list_tasks(status="pending")
- "Mark task 3 done" → complete_task(task_id=3)
- "Delete the groceries task" → list_tasks first to find ID, then delete_task
- "Change task 1 to call mom" → update_task(task_id=1, title="call mom")

CONSTRAINTS:
- You can only manage tasks for the current user (user_id is provided automatically)
- You cannot access other users' tasks
- You cannot perform actions outside of task management
```

---

## Intent Recognition Rules

The agent MUST recognize the following intents and map them to appropriate tool calls:

### 1. Task Creation Intent

**Trigger Patterns**:
- "Add a task to [description]"
- "Create a task [description]"
- "I need to [description]"
- "Remind me to [description]"
- "I have to [description]"
- "Don't let me forget to [description]"
- "[description]" (when clearly a task, not a query)

**Required Tool**: `add_task`

**Parameter Extraction**:
- Title: Extract the main action/item from the natural language
- Description: Extract additional details if provided explicitly

**Examples**:
| User Input | Tool Call |
|------------|-----------|
| "Add a task to buy groceries" | `add_task(title="buy groceries")` |
| "I need to finish the report" | `add_task(title="finish the report")` |
| "Add task: call mom, description: about her birthday" | `add_task(title="call mom", description="about her birthday")` |

---

### 2. Task Listing Intent

**Trigger Patterns**:
- "Show me [my/all] tasks"
- "List [my/all] tasks"
- "What [are my/do I have] tasks?"
- "What's pending?"
- "What have I completed?"
- "Show pending/completed tasks"
- "What do I need to do?"

**Required Tool**: `list_tasks`

**Parameter Extraction**:
- Status: Determine filter from keywords
  - "pending", "incomplete", "not done", "left" → `status="pending"`
  - "completed", "done", "finished" → `status="completed"`
  - "all", no qualifier → `status="all"`

**Examples**:
| User Input | Tool Call |
|------------|-----------|
| "Show me all my tasks" | `list_tasks(status="all")` |
| "What's pending?" | `list_tasks(status="pending")` |
| "What have I completed?" | `list_tasks(status="completed")` |

---

### 3. Task Completion Intent

**Trigger Patterns**:
- "Mark task [ID] [as] complete/done"
- "Complete task [ID]"
- "I finished [task reference]"
- "Done with [task reference]"
- "[task reference] is done"
- "Check off [task reference]"

**Required Tool**: `complete_task`

**Parameter Extraction**:
- Task ID: Extract numeric ID if provided
- Task Reference: If title/description referenced, call `list_tasks` first

**Examples**:
| User Input | Tool Call Sequence |
|------------|-------------------|
| "Mark task 3 as complete" | `complete_task(task_id=3)` |
| "I finished the groceries task" | `list_tasks()` → identify ID → `complete_task(task_id=N)` |
| "Done with task 5" | `complete_task(task_id=5)` |

---

### 4. Task Deletion Intent

**Trigger Patterns**:
- "Delete task [ID]"
- "Remove task [ID]"
- "Delete [task reference]"
- "Get rid of [task reference]"
- "Remove [task reference]"
- "Cancel [task reference]"

**Required Tool**: `delete_task`

**Parameter Extraction**:
- Task ID: Extract numeric ID if provided
- Task Reference: If title referenced, call `list_tasks` first

**Examples**:
| User Input | Tool Call Sequence |
|------------|-------------------|
| "Delete task 5" | `delete_task(task_id=5)` |
| "Remove the meeting task" | `list_tasks()` → identify ID → `delete_task(task_id=N)` |

---

### 5. Task Update Intent

**Trigger Patterns**:
- "Change task [ID] to [new value]"
- "Update task [ID] [field] to [value]"
- "Rename task [ID] to [new title]"
- "Edit [task reference]"
- "Modify [task reference]"

**Required Tool**: `update_task`

**Parameter Extraction**:
- Task ID: Extract or resolve from reference
- Title: New title if changing name
- Description: New description if updating details

**Examples**:
| User Input | Tool Call |
|------------|-----------|
| "Change task 1 to call mom tonight" | `update_task(task_id=1, title="call mom tonight")` |
| "Update task 2 description to include charts" | `update_task(task_id=2, description="include charts")` |

---

## Ambiguity Resolution Protocol

When user input is ambiguous, the agent MUST follow this protocol:

### 1. Task Reference Ambiguity

**Condition**: User references a task by title/description without explicit ID

**Protocol**:
1. Call `list_tasks(status="all")` to retrieve all tasks
2. Identify matching task(s) by title/description similarity
3. If exactly one match: proceed with operation
4. If multiple matches: list options and ask user to specify by ID
5. If no matches: inform user and suggest alternatives

**Example**:
```
User: "Delete the meeting task"

Agent Internal:
1. Call list_tasks() → returns [Task(1, "team meeting"), Task(4, "meeting notes")]
2. Multiple matches found

Agent Response:
"I found multiple tasks related to 'meeting':
1. Task #1: team meeting
4. Task #4: meeting notes
Which one would you like me to delete?"
```

### 2. Operation Ambiguity

**Condition**: User intent is unclear (could be multiple operations)

**Protocol**:
1. Ask clarifying question
2. Provide options based on possible interpretations

**Example**:
```
User: "milk"

Agent Response:
"I'm not sure what you'd like me to do. Would you like me to:
1. Add 'milk' as a new task?
2. Search for tasks mentioning 'milk'?
Please let me know!"
```

### 3. Missing Information

**Condition**: Required information is missing for an operation

**Protocol**:
1. Identify what's missing
2. Ask specifically for the missing information

**Example**:
```
User: "Update task 3"

Agent Response:
"I can update task 3. What would you like to change? You can update:
- The title
- The description
Please tell me what you'd like the new value to be."
```

---

## Response Formatting Rules

### Confirmation Messages

After successful operations, the agent MUST confirm with a natural language response:

| Operation | Confirmation Template |
|-----------|----------------------|
| add_task | "I've added '[title]' to your tasks." |
| list_tasks | "[N] tasks found: [formatted list]" |
| complete_task | "Great! I've marked '[title]' as complete." |
| delete_task | "Done! I've removed '[title]' from your tasks." |
| update_task | "I've updated task #[ID]. [describe change]" |

### Error Messages

When operations fail, the agent MUST provide helpful error messages:

| Error Condition | Response Template |
|-----------------|------------------|
| Task not found | "I couldn't find task #[ID]. Would you like me to list your tasks?" |
| No tasks exist | "You don't have any tasks yet. Would you like to add one?" |
| Invalid input | "I didn't understand that. Could you rephrase?" |
| Tool error | "Something went wrong while [operation]. Please try again." |

### Task List Formatting

When listing tasks, use this format:

```
You have [N] [status] task(s):

1. [Title] [✓ if completed]
   ID: #[ID]
   [Description if exists]

2. [Title] [✓ if completed]
   ID: #[ID]
   [Description if exists]
```

---

## Tool Call Chaining

The agent MAY chain multiple tool calls in a single turn when necessary:

### Allowed Chains

1. **List → Complete**: When user references task by title
   ```
   User: "Complete the groceries task"
   Chain: list_tasks() → complete_task(task_id=found_id)
   ```

2. **List → Delete**: When user references task by title
   ```
   User: "Delete my meeting task"
   Chain: list_tasks() → delete_task(task_id=found_id)
   ```

3. **List → Update**: When user references task by title
   ```
   User: "Rename the report task to quarterly report"
   Chain: list_tasks() → update_task(task_id=found_id, title="quarterly report")
   ```

### Prohibited Chains

1. **Multiple Modifications Without Confirmation**: Do not delete multiple tasks without explicit user confirmation
2. **Assumption Chains**: Do not assume intent and chain operations without verification

---

## Behavioral Constraints

### MUST DO

1. Always use tools for data operations - never fabricate responses
2. Always confirm actions after completion
3. Always ask for clarification when ambiguous
4. Always include task IDs in responses for user reference
5. Always validate tool responses before confirming to user

### MUST NOT DO

1. Never claim to have created/modified/deleted a task without calling the appropriate tool
2. Never access database directly
3. Never expose internal errors or stack traces to users
4. Never perform destructive operations on ambiguous references without confirmation
5. Never assume task IDs - always verify or retrieve them

---

## Conversation Context

The agent receives conversation history as a list of prior messages. The agent SHOULD:

1. Reference prior context when relevant ("As I mentioned earlier...")
2. Maintain consistency with prior statements
3. Use conversation history to resolve ambiguous references ("that task" → last mentioned task)

The agent SHOULD NOT:

1. Repeat information unnecessarily
2. Lose track of multi-turn conversations
3. Contradict prior statements without explanation

---

## Natural Language Pattern Coverage

The agent MUST correctly handle all of the following input patterns:

### Task Creation
- "Add a task to buy groceries"
- "Create a task to finish the report"
- "I need to call mom"
- "Remind me to pay bills"
- "Don't let me forget the meeting"
- "I have to submit the application"

### Task Listing
- "Show me all my tasks"
- "What are my tasks?"
- "List my tasks"
- "What's pending?"
- "What have I completed?"
- "What do I need to do?"
- "Show pending tasks"
- "Show completed tasks"

### Task Completion
- "Mark task 3 as complete"
- "Complete task 5"
- "I finished the groceries task"
- "Done with task 2"
- "Check off the meeting task"
- "Task 1 is done"

### Task Deletion
- "Delete task 3"
- "Remove task 5"
- "Delete the meeting task"
- "Get rid of the groceries task"
- "Cancel the report task"

### Task Update
- "Change task 1 to call mom tonight"
- "Update task 2's description"
- "Rename task 3 to something else"
- "Edit the meeting task title to team standup"
