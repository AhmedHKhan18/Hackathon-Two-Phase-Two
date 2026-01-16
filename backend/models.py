"""SQLModel models for the Todo application."""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    pass


# ============================================================================
# Enums
# ============================================================================

class MessageRole(str, Enum):
    """Enum for chat message roles."""
    USER = "user"
    ASSISTANT = "assistant"


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


# ============================================================================
# Phase III: Conversation Models
# ============================================================================

class Conversation(SQLModel, table=True):
    """Conversation database model for chat sessions."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(max_length=255, index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    # Relationship to messages
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class Message(SQLModel, table=True):
    """Message database model for individual chat messages."""
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id", index=True)
    user_id: str = Field(max_length=255, index=True)
    role: MessageRole = Field(default=MessageRole.USER)
    content: str = Field(max_length=10000)  # Allow longer content for assistant responses
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    # Relationship to conversation
    conversation: Optional[Conversation] = Relationship(back_populates="messages")


# ============================================================================
# Phase III: Chat Request/Response Schemas
# ============================================================================

class ChatRequest(SQLModel):
    """Request model for chat endpoint."""
    message: str = Field(max_length=2000)
    conversation_id: Optional[int] = None


class ToolCall(SQLModel):
    """Model for a single tool call made by the agent."""
    tool_name: str
    arguments: dict
    result: dict


class ChatResponse(SQLModel):
    """Response model for chat endpoint."""
    conversation_id: int
    response: str
    tool_calls: List[ToolCall] = []


class ConversationResponse(SQLModel):
    """Response model for conversation listing."""
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    preview: Optional[str] = None  # First message preview


class ConversationDetailResponse(SQLModel):
    """Response model for conversation with messages."""
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime
    messages: List["MessageResponse"] = []


class MessageResponse(SQLModel):
    """Response model for a message."""
    id: int
    role: MessageRole
    content: str
    created_at: datetime
