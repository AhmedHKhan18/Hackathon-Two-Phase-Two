"""Chat API router for conversation endpoints.

Provides endpoints for chat interaction, conversation listing,
and conversation management.
"""

from typing import List
from fastapi import APIRouter, HTTPException, Depends

import sys
sys.path.insert(0, '..')

from auth import get_current_user, verify_user_access
from models import (
    ChatRequest,
    ChatResponse,
    ToolCall,
    ConversationResponse,
    ConversationDetailResponse,
    MessageResponse,
    DeleteResponse
)
from .services import (
    get_or_create_conversation,
    load_conversation_history,
    store_user_message,
    store_assistant_message,
    list_conversations,
    get_conversation_with_messages,
    delete_conversation
)
from agent.runner import run_agent


router = APIRouter(tags=["chat"])


@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat(
    user_id: str,
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """Process a chat message and return agent response.

    Flow:
    1. Validate user access
    2. Get or create conversation
    3. Load conversation history
    4. Store user message
    5. Run agent with message and history
    6. Store assistant response
    7. Return response with tool calls

    Args:
        user_id: The user ID from URL path
        request: ChatRequest with message and optional conversation_id
        current_user: Authenticated user from JWT

    Returns:
        ChatResponse with conversation_id, response, and tool_calls
    """
    # Verify user access (JWT user_id must match route user_id)
    verify_user_access(current_user, user_id)

    # Validate message
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message is required")

    if len(request.message) > 2000:
        raise HTTPException(
            status_code=400,
            detail="Message must be 2000 characters or less"
        )

    try:
        # Get or create conversation
        conversation = get_or_create_conversation(
            request.conversation_id,
            user_id
        )

        # Load conversation history for context
        history = load_conversation_history(conversation.id, user_id)

        # Store user message before processing
        store_user_message(conversation.id, user_id, request.message.strip())

        # Run the AI agent
        result = run_agent(
            user_message=request.message.strip(),
            user_id=user_id,
            conversation_history=history
        )

        # Store assistant response
        store_assistant_message(conversation.id, user_id, result["response"])

        # Build response with tool calls
        tool_calls = [
            ToolCall(
                tool_name=tc["tool_name"],
                arguments=tc["arguments"],
                result=tc["result"]
            )
            for tc in result.get("tool_calls", [])
        ]

        return ChatResponse(
            conversation_id=conversation.id,
            response=result["response"],
            tool_calls=tool_calls
        )

    except HTTPException:
        raise
    except Exception as e:
        # Log the error with full details
        import traceback
        print(f"Chat error: {str(e)}")
        print(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Chat error: {str(e)}"
        )


@router.get("/{user_id}/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """List all conversations for the authenticated user.

    Args:
        user_id: The user ID from URL path
        current_user: Authenticated user from JWT

    Returns:
        List of ConversationResponse objects
    """
    verify_user_access(current_user, user_id)

    conversations = list_conversations(user_id)

    return [
        ConversationResponse(
            id=conv["id"],
            user_id=conv["user_id"],
            created_at=conv["created_at"],
            updated_at=conv["updated_at"],
            message_count=conv["message_count"],
            preview=conv["preview"]
        )
        for conv in conversations
    ]


@router.get("/{user_id}/conversations/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation_detail(
    user_id: str,
    conversation_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get a conversation with all its messages.

    Args:
        user_id: The user ID from URL path
        conversation_id: The conversation ID to retrieve
        current_user: Authenticated user from JWT

    Returns:
        ConversationDetailResponse with messages
    """
    verify_user_access(current_user, user_id)

    conversation = get_conversation_with_messages(conversation_id, user_id)

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return ConversationDetailResponse(
        id=conversation["id"],
        user_id=conversation["user_id"],
        created_at=conversation["created_at"],
        updated_at=conversation["updated_at"],
        messages=[
            MessageResponse(
                id=msg["id"],
                role=msg["role"],
                content=msg["content"],
                created_at=msg["created_at"]
            )
            for msg in conversation["messages"]
        ]
    )


@router.delete("/{user_id}/conversations/{conversation_id}", response_model=DeleteResponse)
async def delete_conversation_endpoint(
    user_id: str,
    conversation_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Delete a conversation and all its messages.

    Args:
        user_id: The user ID from URL path
        conversation_id: The conversation ID to delete
        current_user: Authenticated user from JWT

    Returns:
        DeleteResponse confirming deletion
    """
    verify_user_access(current_user, user_id)

    deleted = delete_conversation(conversation_id, user_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return DeleteResponse(deleted=True)
