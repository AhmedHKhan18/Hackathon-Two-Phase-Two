"""Database connection module for Neon PostgreSQL via SQLModel."""

import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session

load_dotenv()

# Support both DATABASE_URL and POSTGRES_URL (Vercel's Neon integration)
DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL or POSTGRES_URL environment variable is not set")

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL debugging
    pool_pre_ping=True,  # Verify connections before use
)


def create_db_and_tables() -> None:
    """Create all database tables from SQLModel metadata."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency for FastAPI route handlers to get a database session."""
    with Session(engine) as session:
        yield session
