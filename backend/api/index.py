"""Vercel serverless function entry point for FastAPI."""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import create_db_and_tables
from routes.tasks import router as tasks_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown events."""
    create_db_and_tables()
    yield


app = FastAPI(
    title="Todo API",
    description="RESTful API for Phase II Todo Application with JWT authentication",
    version="1.0.0",
    lifespan=lifespan
)

# Get allowed origins from environment or use defaults
FRONTEND_URL = os.getenv("FRONTEND_URL", "")
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Add production frontend URL if configured
if FRONTEND_URL:
    allowed_origins.append(FRONTEND_URL)
    # Also add without trailing slash if present
    if FRONTEND_URL.endswith("/"):
        allowed_origins.append(FRONTEND_URL.rstrip("/"))
    else:
        allowed_origins.append(FRONTEND_URL + "/")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tasks_router, prefix="/api")


@app.get("/")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": "1.0.0"}


# Export the app for Vercel
handler = app
