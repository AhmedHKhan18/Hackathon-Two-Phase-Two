# Spec-Kit Plus Development Workflow

## Overview

Spec-Kit Plus organizes project specifications in a structured, hierarchical format that enables spec-driven development with Claude Code.

## Spec Organization

```text
specs/
├── overview.md           # Project overview and current phase
├── architecture.md       # System design and technical decisions
├── features/            # Feature specifications
│   ├── task-crud.md
│   ├── authentication.md
│   └── chatbot.md
├── api/                 # API specifications
│   ├── rest-endpoints.md
│   └── mcp-tools.md
├── database/            # Database specifications
│   └── schema.md
└── ui/                  # UI specifications
    ├── components.md
    └── pages.md
```

## Configuration

`.spec-kit/config.yaml` defines project structure and phases:

```yaml
name: project-name
version: "1.0"

structure:
  specs_dir: specs
  features_dir: specs/features
  api_dir: specs/api
  database_dir: specs/database
  ui_dir: specs/ui

phases:
  - name: phase1-console
    features: [task-crud]
  - name: phase2-web
    features: [task-crud, authentication]
  - name: phase3-chatbot
    features: [task-crud, authentication, chatbot]
```

## Development Workflow

### 1. Read Spec Before Implementing

Always reference the spec first:

```text
@specs/features/task-crud.md implement the create task feature
```

This loads:

- Feature specification (user stories, acceptance criteria)
- Related API specs (`@specs/api/rest-endpoints.md`)
- Database schema (`@specs/database/schema.md`)
- UI specs if applicable (`@specs/ui/components.md`)

### 2. Follow Layered CLAUDE.md Context

Load context from multiple levels:

| Level | File | Purpose |
|-------|------|---------|
| Root | `@CLAUDE.md` | Project overview, navigation |
| Frontend | `@frontend/CLAUDE.md` | Next.js patterns |
| Backend | `@backend/CLAUDE.md` | FastAPI patterns |

### 3. Implement Feature Across Stack

**Backend First:**

1. Read `@specs/database/schema.md` → Create models
2. Read `@specs/api/rest-endpoints.md` → Implement routes
3. Follow `@backend/CLAUDE.md` conventions

**Frontend Second:**

1. Read `@specs/ui/components.md` → Build components
2. Read `@specs/api/rest-endpoints.md` → Update API client
3. Follow `@frontend/CLAUDE.md` conventions

### 4. Update Specs When Requirements Change

If requirements change during implementation:

1. Update the relevant spec file first
2. Then implement the changes
3. Keep specs in sync with code

## Spec File Formats

### Feature Spec Template

```markdown
# Feature: [Feature Name]

## User Stories
- As a [role], I can [action] so that [benefit]

## Acceptance Criteria

### [Sub-feature 1]
- Criterion 1
- Criterion 2

### [Sub-feature 2]
- Criterion 1
- Criterion 2

## Technical Notes
- Implementation details
- Edge cases to handle
```

### API Spec Template

````markdown
# REST API Endpoints

## Base URL
- Development: http://localhost:8000
- Production: https://api.example.com

## Authentication
All endpoints require JWT token in header:
```
Authorization: Bearer <token>
```

## Endpoints

### GET /api/{user_id}/tasks
List all tasks for authenticated user.

**Query Parameters:**
- status: "all" | "pending" | "completed"

**Response:**
```json
[
  {
    "id": 1,
    "title": "Task title",
    "completed": false
  }
]
```

### POST /api/{user_id}/tasks
Create a new task.

**Request Body:**
```json
{
  "title": "Task title",
  "description": "Optional description"
}
```

**Response:** Created Task object
````

### Database Spec Template

```markdown
# Database Schema

## Tables

### users (managed by Better Auth)
- id: string (primary key)
- email: string (unique)
- name: string
- created_at: timestamp

### tasks
- id: integer (primary key)
- user_id: string (foreign key → users.id)
- title: string (not null, max 200)
- description: text (nullable, max 1000)
- completed: boolean (default false)
- created_at: timestamp
- updated_at: timestamp

## Indexes
- tasks.user_id (for filtering by user)
- tasks.completed (for status filtering)

## Relationships
- tasks.user_id → users.id (many-to-one)
```

## Referencing Specs

### In Claude Code Prompts

```bash
# Single spec
@specs/features/authentication.md implement user login

# Multiple specs
@specs/features/task-crud.md @specs/api/rest-endpoints.md implement the API

# Full feature across stack
@specs/features/authentication.md implement complete auth flow including frontend and backend
```

### From CLAUDE.md Files

```markdown
## How to Use Specs

1. Always read relevant spec before implementing
2. Reference specs with: @specs/features/task-crud.md
3. Update specs if requirements change

## Development Workflow

1. Read spec: @specs/features/[feature].md
2. Implement backend: @backend/CLAUDE.md
3. Implement frontend: @frontend/CLAUDE.md
4. Test and iterate
```

## Spec-First Benefits

| Benefit | Description |
|---------|-------------|
| Clear Requirements | User stories and acceptance criteria defined upfront |
| API Contracts | Frontend and backend agree on endpoints before coding |
| Single Source of Truth | All team members reference same specs |
| Easy Updates | Change spec, then update code consistently |
| Context for Claude | Specs provide clear instructions for AI-assisted development |

## Common Workflows

### Adding a New Feature

1. Write feature spec: `specs/features/new-feature.md`
2. Define API endpoints: `specs/api/rest-endpoints.md`
3. Design database schema: `specs/database/schema.md`
4. Plan UI components: `specs/ui/components.md`
5. Implement with: `@specs/features/new-feature.md implement`

### Modifying Existing Feature

1. Update relevant specs first
2. Reference updated spec in implementation prompt
3. Claude Code reads updated spec and modifies code accordingly

### Cross-Cutting Changes

```bash
@specs/features/authentication.md add password reset feature across frontend and backend
```

Claude Code reads:

- Feature spec for requirements
- API spec for new endpoints
- Database spec for any schema changes
- UI spec for new components
- Both CLAUDE.md files for patterns

## Best Practices

### Spec Writing

- Be specific and testable
- Include examples (requests/responses for APIs)
- Define edge cases and error handling
- Keep specs focused (one feature per file)

### Spec Organization

- Group related specs in subdirectories
- Use consistent naming conventions
- Reference related specs when needed
- Keep specs under 500 lines (split if longer)

### Implementation

- Always read spec first
- Follow spec exactly for MVP
- Flag ambiguities for clarification
- Update spec if requirements change during implementation

## Integration with Claude Code

### Why Spec-Kit Plus Works with Claude Code

| Feature | Benefit |
|---------|---------|
| Structured Context | Organized specs are easier to reference |
| Progressive Disclosure | Load only relevant specs |
| Consistent Format | Claude learns patterns quickly |
| Monorepo Support | Works across frontend/backend |
| Clear Triggers | File paths indicate what to load |

### Example Session

```text
You: Let's build the task CRUD feature

Claude: I'll read @specs/features/task-crud.md first
[reads spec]

Claude: I see we need:
- Backend: SQLModel Task model, 5 API endpoints
- Frontend: TaskList component, API client methods
- Let's start with the backend...
[implements based on spec]
```

## Troubleshooting

### Issue: Claude doesn't find the spec

- Check file path: `@specs/features/file.md` (not `@/specs/...`)
- Verify file exists in specs directory
- Check `.spec-kit/config.yaml` paths

### Issue: Implementation doesn't match spec

- Re-read spec and point out discrepancies
- Update spec if requirements changed
- Clarify ambiguous requirements

### Issue: Specs out of sync with code

- Review all related specs
- Update specs to match current implementation
- Use specs as single source of truth going forward
