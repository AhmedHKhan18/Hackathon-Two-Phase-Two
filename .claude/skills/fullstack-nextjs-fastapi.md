# Full-Stack Next.js + FastAPI Development

## Overview

Build full-stack features across Next.js 16+ frontend and FastAPI backend within a monorepo structure.

## Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 16+ (App Router), TypeScript, Tailwind CSS |
| Backend | FastAPI, SQLModel ORM, Python |
| Database | PostgreSQL (Neon Serverless) |
| Auth | Better Auth with JWT tokens |

## Monorepo Structure

```text
project/
├── frontend/          # Next.js application
│   ├── app/          # App Router pages
│   ├── components/   # React components
│   ├── lib/          # Utilities and API client
│   └── CLAUDE.md     # Frontend guidelines
├── backend/          # FastAPI application
│   ├── main.py       # App entry point
│   ├── models.py     # SQLModel models
│   ├── routes/       # API endpoints
│   └── CLAUDE.md     # Backend guidelines
├── specs/            # Specifications
└── CLAUDE.md         # Root guidelines
```

## Development Workflow

### 1. Read Specifications First

Always read relevant specs before implementing:

- `@specs/features/[feature].md` - What to build
- `@specs/api/rest-endpoints.md` - API contracts
- `@specs/database/schema.md` - Database models
- `@specs/ui/[component].md` - UI specifications

### 2. Implement Backend First

**Database Models** (`backend/models.py`):

```python
from sqlmodel import SQLModel, Field
from datetime import datetime

class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id")
    title: str = Field(max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**API Routes** (`backend/routes/tasks.py`):

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

router = APIRouter(prefix="/api/{user_id}/tasks")

@router.get("/")
async def list_tasks(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Verify user_id matches authenticated user
    if user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Filter by authenticated user
    statement = select(Task).where(Task.user_id == user_id)
    tasks = session.exec(statement).all()
    return tasks
```

### 3. Implement Frontend

**API Client** (`frontend/lib/api.ts`):

```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function getAuthToken(): Promise<string> {
  // Get JWT token from Better Auth session
  const session = await auth.api.getSession();
  return session.token;
}

export const api = {
  async getTasks(userId: string) {
    const token = await getAuthToken();
    const res = await fetch(`${API_BASE}/api/${userId}/tasks`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    if (!res.ok) throw new Error('Failed to fetch tasks');
    return res.json();
  },

  async createTask(userId: string, data: { title: string; description?: string }) {
    const token = await getAuthToken();
    const res = await fetch(`${API_BASE}/api/${userId}/tasks`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to create task');
    return res.json();
  },
};
```

**React Components** (`frontend/components/TaskList.tsx`):

```typescript
'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

export function TaskList({ userId }: { userId: string }) {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getTasks(userId)
      .then(setTasks)
      .finally(() => setLoading(false));
  }, [userId]);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="space-y-2">
      {tasks.map(task => (
        <div key={task.id} className="p-4 border rounded">
          <h3 className="font-medium">{task.title}</h3>
          {task.description && <p className="text-sm text-gray-600">{task.description}</p>}
        </div>
      ))}
    </div>
  );
}
```

## Key Patterns

### Next.js App Router

- Use Server Components by default
- Add `'use client'` only when needed (state, effects, event handlers)
- Server Actions for mutations when appropriate

### API Communication

- All backend calls go through `/lib/api.ts`
- Always include JWT token in `Authorization: Bearer <token>` header
- Handle errors consistently

### Database Operations

- Use SQLModel for all database operations
- Always filter queries by authenticated `user_id`
- Use transactions for multi-step operations

### Styling

- Use Tailwind CSS utility classes
- Follow existing component patterns
- No inline styles

## Security Checklist

- [ ] All API endpoints verify JWT token
- [ ] User ID in URL matches authenticated user
- [ ] Database queries filter by `user_id`
- [ ] Sensitive data never exposed in API responses
- [ ] Environment variables used for secrets

## Common Tasks

### Adding a New Feature

1. Read `@specs/features/[feature].md`
2. Create/update database model in `backend/models.py`
3. Add API routes in `backend/routes/[feature].py`
4. Update API client in `frontend/lib/api.ts`
5. Create UI components in `frontend/components/`
6. Add pages in `frontend/app/`

### Testing Integration

1. Start backend: `cd backend && uvicorn main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Test authentication flow
4. Verify API requests include JWT token
5. Check user data isolation

## References

- Read `@frontend/CLAUDE.md` for frontend-specific patterns
- Read `@backend/CLAUDE.md` for backend-specific patterns
- Read `@CLAUDE.md` for project overview and navigation
