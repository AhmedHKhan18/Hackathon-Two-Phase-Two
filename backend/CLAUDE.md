# Backend Development Rules

## Technology Stack
- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLModel
- **Database**: Neon PostgreSQL
- **Auth**: JWT verification via python-jose (HS256)
- **Package Manager**: uv (preferred over pip)

## Environment Variables Required
- `DATABASE_URL`: Neon PostgreSQL connection string
- `BETTER_AUTH_SECRET`: Shared JWT signing secret (must match frontend)

## Project Structure
```
backend/
├── main.py          # FastAPI app entry point
├── auth.py          # JWT verification utilities
├── database.py      # Database connection
├── models.py        # SQLModel models
├── routes/
│   └── tasks.py     # Task CRUD endpoints
├── pyproject.toml   # Project config and dependencies
├── requirements.txt # Python dependencies (legacy)
├── .venv/           # Virtual environment (not in git)
└── .env             # Environment variables (not in git)
```

## API Design Rules
- All task endpoints under `/api/{user_id}/tasks`
- JWT token required in Authorization header
- Verify JWT user_id matches route user_id
- Return appropriate HTTP status codes (200, 201, 400, 401, 403, 404, 500)

## Security Rules
- Never trust user_id from request body - always use JWT sub claim
- All queries must filter by user_id
- Return 404 (not 403) for non-existent tasks to prevent enumeration
- Shared secret must be minimum 32 characters

## Code Standards
- Use type hints on all functions
- Use Pydantic/SQLModel for request/response validation
- Use HTTPException for error handling
- Use dependency injection for auth context
