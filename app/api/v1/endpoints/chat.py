import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatHistoryResponse,
)
from app.crud import crud_chat
from app.services.ai_chat_service import AIChatService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/history",
    response_model=ChatHistoryResponse,
    summary="Get user's chat history with Agent IA DGDA",
)
async def get_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves all past chat messages between the current user and Agent IA DGDA."""
    messages = await crud_chat.get_chat_history(db=db, user_id=current_user.id)
    return ChatHistoryResponse(
        messages=[ChatMessageResponse.from_orm(m) for m in messages]
    )


@router.post(
    "/message",
    response_model=ChatMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a message to Agent IA DGDA and receive intelligent response",
)
async def send_message(
    payload: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Sends a question or prompt to Agent IA DGDA.
    1. Saves the user's message to the conversation history.
    2. Passes the query + context to OpenAI LLM (or customs intelligence fallback).
    3. Saves the assistant's authoritative answer to the database.
    4. Returns the response with legal reference and category metadata.
    """
    user_text = payload.message.strip()
    if not user_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty",
        )

    # 1. Save user message to database
    await crud_chat.save_chat_message(
        db=db,
        user_id=current_user.id,
        role="user",
        content=user_text,
    )

    # 2. Retrieve recent history for context
    past_messages = await crud_chat.get_chat_history(db=db, user_id=current_user.id)

    # 3. Generate response via AI Service (OpenAI with DGDA RAG / Knowledge fallback)
    ai_result = await AIChatService.generate_response(
        user_message=user_text,
        conversation_history=past_messages,
    )

    # 4. Save assistant response to database
    assistant_msg = await crud_chat.save_chat_message(
        db=db,
        user_id=current_user.id,
        role="assistant",
        content=ai_result["reply"],
        legal_reference=ai_result.get("legal_reference"),
        category=ai_result.get("category"),
    )

    return ChatMessageResponse.from_orm(assistant_msg)


@router.delete(
    "/history",
    status_code=status.HTTP_200_OK,
    summary="Clear conversation history",
)
async def clear_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Clears all conversation history for the current user and resets with initial greeting."""
    await crud_chat.clear_chat_history(db=db, user_id=current_user.id)
    # Re-fetch will seed initial welcome message
    welcome_messages = await crud_chat.get_chat_history(db=db, user_id=current_user.id)
    return {
        "success": True,
        "message": "Chat history cleared successfully",
        "initial_message": ChatMessageResponse.from_orm(welcome_messages[0]),
    }
