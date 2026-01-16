"""Chat services for conversation and message management.

Handles database operations for conversations and messages,
ensuring stateless operation by persisting all state.
"""

from datetime import datetime, timezone
from typing import List, Optional, Dict
from sqlmodel import Session, select

import sys
sys.path.insert(0, '..')

from database import engine
from models import Conversation, Message, MessageRole, MessageResponse


def create_conversation(user_id: str) -> Conversation:
    """Create a new conversation for a user.

    Args:
        user_id: The user ID who owns this conversation

    Returns:
        The created Conversation object
    """
    with Session(engine) as session:
        conversation = Conversation(
            user_id=user_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        return conversation


def get_conversation(conversation_id: int, user_id: str) -> Optional[Conversation]:
    """Get a conversation by ID with user ownership check.

    Args:
        conversation_id: The conversation ID to retrieve
        user_id: The user ID for ownership verification

    Returns:
        Conversation if found and owned by user, None otherwise
    """
    with Session(engine) as session:
        conversation = session.exec(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        ).first()
        return conversation


def get_or_create_conversation(
    conversation_id: Optional[int],
    user_id: str
) -> Conversation:
    """Get existing conversation or create a new one.

    Args:
        conversation_id: Optional ID of existing conversation
        user_id: The user ID

    Returns:
        Existing or newly created Conversation
    """
    if conversation_id:
        conversation = get_conversation(conversation_id, user_id)
        if conversation:
            return conversation
        # If conversation not found, create new one
    return create_conversation(user_id)


def load_conversation_history(
    conversation_id: int,
    user_id: str,
    limit: int = 100
) -> List[Dict[str, str]]:
    """Load conversation history for agent context.

    Args:
        conversation_id: The conversation to load
        user_id: The user ID for ownership verification
        limit: Maximum number of messages to load (default 100)

    Returns:
        List of message dicts in OpenAI format [{role, content}]
    """
    with Session(engine) as session:
        # Verify conversation ownership
        conversation = session.exec(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        ).first()

        if not conversation:
            return []

        # Load messages ordered by created_at ascending (oldest first)
        messages = session.exec(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
        ).all()

        return [
            {"role": msg.role.value, "content": msg.content}
            for msg in messages
        ]


def store_user_message(
    conversation_id: int,
    user_id: str,
    content: str
) -> Message:
    """Store a user message in the database.

    Args:
        conversation_id: The conversation this message belongs to
        user_id: The user who sent the message
        content: The message content

    Returns:
        The created Message object
    """
    with Session(engine) as session:
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=MessageRole.USER,
            content=content,
            created_at=datetime.now(timezone.utc)
        )
        session.add(message)

        # Update conversation timestamp
        conversation = session.get(Conversation, conversation_id)
        if conversation:
            conversation.updated_at = datetime.now(timezone.utc)
            session.add(conversation)

        session.commit()
        session.refresh(message)
        return message


def store_assistant_message(
    conversation_id: int,
    user_id: str,
    content: str
) -> Message:
    """Store an assistant message in the database.

    Args:
        conversation_id: The conversation this message belongs to
        user_id: The user this conversation belongs to
        content: The assistant's response content

    Returns:
        The created Message object
    """
    with Session(engine) as session:
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=MessageRole.ASSISTANT,
            content=content,
            created_at=datetime.now(timezone.utc)
        )
        session.add(message)

        # Update conversation timestamp
        conversation = session.get(Conversation, conversation_id)
        if conversation:
            conversation.updated_at = datetime.now(timezone.utc)
            session.add(conversation)

        session.commit()
        session.refresh(message)
        return message


def list_conversations(user_id: str) -> List[Dict]:
    """List all conversations for a user.

    Args:
        user_id: The user whose conversations to list

    Returns:
        List of conversation dicts with id, timestamps, count, and preview
    """
    with Session(engine) as session:
        conversations = session.exec(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
        ).all()

        result = []
        for conv in conversations:
            # Get message count and first message for preview
            messages = session.exec(
                select(Message)
                .where(Message.conversation_id == conv.id)
                .order_by(Message.created_at.asc())
            ).all()

            preview = None
            if messages:
                # Use first user message as preview
                for msg in messages:
                    if msg.role == MessageRole.USER:
                        preview = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
                        break

            result.append({
                "id": conv.id,
                "user_id": conv.user_id,
                "created_at": conv.created_at,
                "updated_at": conv.updated_at,
                "message_count": len(messages),
                "preview": preview
            })

        return result


def get_conversation_with_messages(
    conversation_id: int,
    user_id: str
) -> Optional[Dict]:
    """Get a conversation with all its messages.

    Args:
        conversation_id: The conversation to retrieve
        user_id: The user ID for ownership verification

    Returns:
        Dict with conversation details and messages, or None if not found
    """
    with Session(engine) as session:
        conversation = session.exec(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        ).first()

        if not conversation:
            return None

        messages = session.exec(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        ).all()

        return {
            "id": conversation.id,
            "user_id": conversation.user_id,
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at,
            "messages": [
                {
                    "id": msg.id,
                    "role": msg.role.value,
                    "content": msg.content,
                    "created_at": msg.created_at
                }
                for msg in messages
            ]
        }


def delete_conversation(conversation_id: int, user_id: str) -> bool:
    """Delete a conversation and all its messages.

    Args:
        conversation_id: The conversation to delete
        user_id: The user ID for ownership verification

    Returns:
        True if deleted, False if not found
    """
    with Session(engine) as session:
        conversation = session.exec(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        ).first()

        if not conversation:
            return False

        # Delete all messages first (cascade should handle this, but be explicit)
        messages = session.exec(
            select(Message).where(Message.conversation_id == conversation_id)
        ).all()

        for msg in messages:
            session.delete(msg)

        session.delete(conversation)
        session.commit()
        return True
