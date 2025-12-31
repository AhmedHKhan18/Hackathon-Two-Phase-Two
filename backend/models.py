"""SQLModel models for the Todo application."""

from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field


class TaskBase(SQLModel):
    """Base model for Task with shared fields."""
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)


class TaskCreate(TaskBase):
    """Request model for creating a task."""
    pass


class TaskUpdate(SQLModel):
    """Request model for updating a task."""
    title: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: Optional[bool] = None


class Task(TaskBase, table=True):
    """Task database model."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(max_length=255, index=True)
    completed: bool = Field(default=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class TaskResponse(TaskBase):
    """Response model for a task."""
    id: int
    user_id: str
    completed: bool
    created_at: datetime
    updated_at: datetime


class DeleteResponse(SQLModel):
    """Response model for delete operations."""
    deleted: bool = True
