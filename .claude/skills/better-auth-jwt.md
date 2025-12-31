# Better Auth + JWT Authentication

## Overview

Better Auth is a TypeScript authentication library for Next.js that can issue JWT tokens. This skill covers integrating Better Auth on the frontend with JWT verification on the FastAPI backend.

## Architecture

```
┌─────────────────┐         JWT Token          ┌──────────────────┐
│  Next.js        │ ────────────────────────> │  FastAPI         │
│  (Better Auth)  │                            │  (JWT Verify)    │
│                 │ <──────────────────────── │                  │
└─────────────────┘    User-specific Data      └──────────────────┘
```

## How It Works

1. **User logs in** → Better Auth creates session and issues JWT token
2. **Frontend makes API call** → Includes JWT in `Authorization: Bearer <token>` header
3. **Backend receives request** → Verifies JWT signature using shared secret
4. **Backend identifies user** → Decodes token to get user ID
5. **Backend filters data** → Returns only data belonging to that user

## Implementation

### 1. Frontend: Better Auth Setup

**Install Dependencies**:
```bash
cd frontend
npm install better-auth @better-auth/react
```

**Create Auth Configuration** (`lib/auth.ts`):
```typescript
import { betterAuth } from "better-auth";
import { nextCookies } from "better-auth/next-js";

export const auth = betterAuth({
  database: {
    provider: "postgresql",
    url: process.env.DATABASE_URL!,
  },
  emailAndPassword: {
    enabled: true,
  },
  // Enable JWT plugin
  plugins: [
    nextCookies(),
  ],
  jwt: {
    enabled: true,
    expiresIn: "7d", // Token expires in 7 days
    secret: process.env.BETTER_AUTH_SECRET!, // Shared secret with backend
  },
});
```

**Environment Variables** (`.env.local`):
```env
DATABASE_URL=postgresql://user:pass@host/db
BETTER_AUTH_SECRET=your-secret-key-here-min-32-chars
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Create Auth Provider** (`components/auth-provider.tsx`):
```typescript
'use client';

import { SessionProvider } from "@better-auth/react";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  return (
    <SessionProvider>
      {children}
    </SessionProvider>
  );
}
```

**Wrap App** (`app/layout.tsx`):
```typescript
import { AuthProvider } from '@/components/auth-provider';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
```

### 2. Frontend: Auth Pages

**Sign Up Page** (`app/signup/page.tsx`):
```typescript
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { auth } from '@/lib/auth';

export default function SignUpPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      await auth.api.signUp({
        email,
        password,
        name,
      });
      router.push('/dashboard');
    } catch (error) {
      console.error('Sign up failed:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-md mx-auto p-6 space-y-4">
      <h1 className="text-2xl font-bold">Sign Up</h1>

      <input
        type="text"
        placeholder="Name"
        value={name}
        onChange={(e) => setName(e.target.value)}
        className="w-full p-2 border rounded"
        required
      />

      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        className="w-full p-2 border rounded"
        required
      />

      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        className="w-full p-2 border rounded"
        required
      />

      <button type="submit" className="w-full bg-blue-500 text-white p-2 rounded">
        Sign Up
      </button>
    </form>
  );
}
```

**Sign In Page** (`app/signin/page.tsx`):
```typescript
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { auth } from '@/lib/auth';

export default function SignInPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      await auth.api.signIn({
        email,
        password,
      });
      router.push('/dashboard');
    } catch (error) {
      console.error('Sign in failed:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-md mx-auto p-6 space-y-4">
      <h1 className="text-2xl font-bold">Sign In</h1>

      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        className="w-full p-2 border rounded"
        required
      />

      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        className="w-full p-2 border rounded"
        required
      />

      <button type="submit" className="w-full bg-blue-500 text-white p-2 rounded">
        Sign In
      </button>
    </form>
  );
}
```

### 3. Frontend: API Client with JWT

**Update API Client** (`lib/api.ts`):
```typescript
import { auth } from './auth';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function getAuthToken(): Promise<string> {
  const session = await auth.api.getSession();
  if (!session?.token) {
    throw new Error('Not authenticated');
  }
  return session.token;
}

async function apiRequest(endpoint: string, options: RequestInit = {}) {
  const token = await getAuthToken();

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Token expired or invalid - redirect to login
      window.location.href = '/signin';
    }
    throw new Error(`API error: ${response.statusText}`);
  }

  return response.json();
}

export const api = {
  async getTasks(userId: string) {
    return apiRequest(`/api/${userId}/tasks`);
  },

  async createTask(userId: string, data: { title: string; description?: string }) {
    return apiRequest(`/api/${userId}/tasks`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async updateTask(userId: string, taskId: number, data: Partial<Task>) {
    return apiRequest(`/api/${userId}/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  async deleteTask(userId: string, taskId: number) {
    return apiRequest(`/api/${userId}/tasks/${taskId}`, {
      method: 'DELETE',
    });
  },
};
```

### 4. Backend: JWT Verification

**Install Dependencies**:
```bash
cd backend
pip install python-jose[cryptography] passlib[bcrypt] --break-system-packages
```

**Create Auth Utilities** (`auth.py`):
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import os

# Must match frontend BETTER_AUTH_SECRET
SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")
ALGORITHM = "HS256"

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify JWT token and return user data"""
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")  # 'sub' is standard JWT field for user ID

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )

        return {
            "id": user_id,
            "email": payload.get("email"),
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

async def get_current_user(user: dict = Depends(verify_token)) -> dict:
    """Get current authenticated user"""
    return user
```

**Environment Variables** (`.env`):
```env
DATABASE_URL=postgresql://user:pass@host/db
BETTER_AUTH_SECRET=your-secret-key-here-min-32-chars
```

### 5. Backend: Protected Routes

**Update API Routes** (`routes/tasks.py`):
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from auth import get_current_user
from database import get_session
from models import Task

router = APIRouter(prefix="/api/{user_id}/tasks")

@router.get("/")
async def list_tasks(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """List all tasks for authenticated user"""

    # Verify URL user_id matches authenticated user
    if user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users' tasks"
        )

    # Filter by authenticated user
    statement = select(Task).where(Task.user_id == user_id)
    tasks = session.exec(statement).all()
    return tasks

@router.post("/")
async def create_task(
    user_id: str,
    task_data: TaskCreate,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Create a new task"""

    # Verify URL user_id matches authenticated user
    if user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create tasks for other users"
        )

    # Create task associated with authenticated user
    task = Task(
        user_id=user_id,
        title=task_data.title,
        description=task_data.description,
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.put("/{task_id}")
async def update_task(
    user_id: str,
    task_id: int,
    task_data: TaskUpdate,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Update a task"""

    # Verify URL user_id matches authenticated user
    if user_id != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    # Find task and verify ownership
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id  # Critical: verify user owns this task
    )
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Update task
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.completed is not None:
        task.completed = task_data.completed

    session.commit()
    session.refresh(task)
    return task

@router.delete("/{task_id}")
async def delete_task(
    user_id: str,
    task_id: int,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Delete a task"""

    # Verify URL user_id matches authenticated user
    if user_id != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    # Find task and verify ownership
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id
    )
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    session.delete(task)
    session.commit()
    return {"deleted": True}
```

## Security Checklist

### Required for All Endpoints

- [ ] Verify JWT token with `Depends(get_current_user)`
- [ ] Check `user_id` in URL matches `current_user["id"]`
- [ ] Filter database queries by `user_id`
- [ ] Return 401 for missing/invalid tokens
- [ ] Return 403 for user ID mismatch
- [ ] Never expose other users' data

### Environment Variables

- [ ] `BETTER_AUTH_SECRET` set in both frontend and backend
- [ ] Secret is at least 32 characters
- [ ] Secret is kept secure (not in git)
- [ ] Same secret used in both services

### Token Configuration

- [ ] Set appropriate expiration (e.g., 7 days)
- [ ] Use HS256 algorithm
- [ ] Include user ID in `sub` claim
- [ ] Include email for convenience

## Common Issues

### "Could not validate credentials"
- Check `BETTER_AUTH_SECRET` matches in both services
- Verify token is being sent in header
- Check token hasn't expired

### "Cannot access other users' tasks"
- Frontend sending wrong `user_id` in URL
- Should use authenticated user's ID from session

### Token not included in requests
- Check `getAuthToken()` is being called
- Verify `Authorization` header is set
- Check session exists before making API call

## Testing Authentication

### Manual Testing

1. Sign up a new user
2. Sign in with credentials
3. Check browser DevTools → Application → Cookies for session
4. Make API request and check Network tab for `Authorization` header
5. Try accessing another user's tasks (should fail with 403)

### Test User Isolation

```python
# Backend test
def test_user_cannot_access_other_tasks():
    # User A creates a task
    task = create_task(user_id="user_a", title="Secret")

    # User B tries to access it
    response = client.get(
        f"/api/user_b/tasks/{task.id}",
        headers={"Authorization": f"Bearer {user_b_token}"}
    )

    assert response.status_code == 404  # Not found (filtered by user_id)
```

## Benefits

1. **User Isolation**: Each user only sees their own data
2. **Stateless Auth**: Backend doesn't need session storage
3. **Token Expiry**: Automatic logout after configured time
4. **Independent Services**: Frontend and backend verify auth independently
5. **Scalable**: No shared session database needed

## Best Practices

- Always verify user_id matches authenticated user
- Set reasonable token expiration (7-30 days)
- Use HTTPS in production
- Rotate `BETTER_AUTH_SECRET` periodically
- Log authentication failures for security monitoring
- Implement refresh token flow for better UX
