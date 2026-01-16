"""FastAPI application entry point."""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from database import create_db_and_tables
from routes.tasks import router as tasks_router
from chat.router import router as chat_router

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown events."""
    # Startup: Create database tables
    create_db_and_tables()
    yield
    # Shutdown: Cleanup (if needed)


app = FastAPI(
    title="Todo API",
    description="RESTful API for Phase III Todo Application with AI Chatbot",
    version="2.0.0",
    lifespan=lifespan
)

# Get allowed origins from environment or use defaults
FRONTEND_URL = os.getenv("FRONTEND_URL", "")
allowed_origins = [
    "http://localhost:3000",  # Next.js dev server
    "http://localhost:3001",
    "http://localhost:3002",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:3002",
]

# Add production frontend URL if configured
if FRONTEND_URL:
    allowed_origins.append(FRONTEND_URL)
    if FRONTEND_URL.endswith("/"):
        allowed_origins.append(FRONTEND_URL.rstrip("/"))
    else:
        allowed_origins.append(FRONTEND_URL + "/")

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tasks_router, prefix="/api")
app.include_router(chat_router, prefix="/api")


@app.get("/")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": "2.0.0", "phase": "III"}


@app.post("/debug/verify-token")
async def debug_verify_token(token: str):
    """Debug endpoint to test token verification."""
    from jose import jwt, JWTError
    import os

    secret = os.getenv("BETTER_AUTH_SECRET")

    result = {
        "secret_loaded": bool(secret),
        "secret_length": len(secret) if secret else 0,
        "secret_preview": secret[:10] + "..." if secret else None,
        "token_length": len(token),
        "token_preview": token[:50] + "..." if len(token) > 50 else token,
    }

    try:
        # Get unverified header and claims
        header = jwt.get_unverified_header(token)
        claims = jwt.get_unverified_claims(token)
        result["header"] = header
        result["claims_unverified"] = claims
    except Exception as e:
        result["decode_error"] = str(e)
        return result

    try:
        # Try to verify
        payload = jwt.decode(token, secret, algorithms=["HS256"], options={"verify_aud": False})
        result["verified"] = True
        result["payload"] = payload
    except JWTError as e:
        result["verified"] = False
        result["verify_error"] = str(e)

    return result
