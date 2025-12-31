# Quickstart: Full-Stack Todo Web Application

**Feature**: 001-fullstack-todo-app
**Date**: 2025-12-30

## Prerequisites

- Node.js 18+ (for frontend)
- Python 3.11+ (for backend)
- PostgreSQL database (Neon recommended)
- Git

## Quick Setup

### 1. Clone and Navigate

```bash
cd hackathon-two-phase-two
```

### 2. Set Up Environment Variables

#### Backend (.env)

Create `backend/.env`:

```env
DATABASE_URL=postgresql://user:password@host/database?sslmode=require
BETTER_AUTH_SECRET=your-secret-key-minimum-32-characters-long
```

#### Frontend (.env.local)

Create `frontend/.env.local`:

```env
DATABASE_URL=postgresql://user:password@host/database?sslmode=require
BETTER_AUTH_SECRET=your-secret-key-minimum-32-characters-long
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Important**: `BETTER_AUTH_SECRET` must be identical in both files.

### 3. Start Backend

```bash
cd backend

# Create virtual environment with uv
uv venv

# Activate virtual environment
# On Windows (PowerShell): .venv\Scripts\Activate.ps1
# On Windows (CMD): .venv\Scripts\activate.bat
# On Unix/macOS: source .venv/bin/activate

# Install dependencies with uv
uv pip install -r requirements.txt
# Or use pyproject.toml: uv sync

# Start server
uvicorn main:app --reload --port 8000
```

Backend runs at: http://localhost:8000

### 4. Start Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs at: http://localhost:3000

## Verify Setup

### 1. Check Backend Health

```bash
curl http://localhost:8000/
```

Expected response:
```json
{"status": "ok", "version": "1.0.0"}
```

### 2. Check Frontend

Open http://localhost:3000 in your browser. You should see the sign-in/sign-up page.

## Test Authentication Flow

1. Navigate to http://localhost:3000/signup
2. Create an account with email and password
3. Verify redirect to dashboard
4. Sign out and sign back in
5. Verify session persists across page refresh

## Test Task Operations

After signing in:

1. Create a task with title "Test task"
2. Verify task appears in list
3. Edit the task title
4. Mark task as complete
5. Delete the task
6. Verify all changes persist after refresh

## Project Structure

```
hackathon-two-phase-two/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── auth.py              # JWT verification
│   ├── database.py          # Database connection
│   ├── models.py            # SQLModel models
│   ├── routes/
│   │   └── tasks.py         # Task endpoints
│   ├── requirements.txt     # Python dependencies
│   └── .env                 # Backend secrets
│
├── frontend/
│   ├── app/                 # Next.js App Router
│   │   ├── layout.tsx       # Root layout
│   │   ├── page.tsx         # Landing page
│   │   ├── signin/          # Sign-in page
│   │   ├── signup/          # Sign-up page
│   │   └── dashboard/       # Task management
│   ├── components/          # React components
│   ├── lib/
│   │   ├── auth.ts          # Better Auth config
│   │   └── api.ts           # API client
│   ├── package.json         # Node dependencies
│   └── .env.local           # Frontend secrets
│
└── specs/
    └── 001-fullstack-todo-app/
        ├── spec.md          # Feature specification
        ├── plan.md          # Implementation plan
        ├── research.md      # Technology decisions
        ├── data-model.md    # Entity definitions
        ├── quickstart.md    # This file
        ├── contracts/       # API contracts
        └── tasks.md         # Implementation tasks
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/api/{user_id}/tasks` | List all tasks |
| POST | `/api/{user_id}/tasks` | Create task |
| GET | `/api/{user_id}/tasks/{id}` | Get single task |
| PUT | `/api/{user_id}/tasks/{id}` | Update task |
| DELETE | `/api/{user_id}/tasks/{id}` | Delete task |
| PATCH | `/api/{user_id}/tasks/{id}/complete` | Toggle completion |

All `/api/*` endpoints require `Authorization: Bearer <JWT>` header.

## Troubleshooting

### "Could not validate credentials" (401)

- Verify `BETTER_AUTH_SECRET` matches in both `.env` files
- Check that the JWT token is being sent in the Authorization header
- Ensure the token hasn't expired

### "Cannot access other users' tasks" (403)

- The `user_id` in the URL must match the authenticated user's ID
- Check that you're using the correct user ID from the session

### Database connection failed

- Verify `DATABASE_URL` is correct in both `.env` files
- Check that the database is accessible (Neon dashboard)
- Ensure SSL mode is enabled for Neon (`?sslmode=require`)

### Frontend can't reach backend

- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check that backend is running on port 8000
- Check CORS configuration in backend

## Development Commands

### Backend

```bash
# Start with auto-reload
uvicorn main:app --reload

# Run on specific port
uvicorn main:app --reload --port 8000

# Check logs
# (logs appear in terminal)
```

### Frontend

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Type check
npm run lint
```

## Next Steps

After setup is complete:

1. Review the [implementation plan](./plan.md)
2. Check the [task list](./tasks.md) for implementation order
3. Follow the task implementation sequence exactly
4. Validate each feature against acceptance criteria
