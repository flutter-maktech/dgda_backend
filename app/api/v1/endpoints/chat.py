import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_current_active_staff, get_db
from app.models.user import User
from app.schemas.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatHistoryResponse,
    KnowledgeEntryCreate,
    KnowledgeEntryUpdate,
    KnowledgeEntryResponse,
    TestAgentQueryRequest,
    TestAgentQueryResponse,
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
    2. Passes the query + context to AI engine (Gemini/OpenAI/DGDA domain knowledge).
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

    # 3. Generate response via AI Service
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
    welcome_messages = await crud_chat.get_chat_history(db=db, user_id=current_user.id)
    return {
        "success": True,
        "message": "Chat history cleared successfully",
        "initial_message": ChatMessageResponse.from_orm(welcome_messages[0]),
    }


# ─────────────────────────────────────────────────────────────────────────────
# AI KNOWLEDGE TRAINER & RAG MANAGEMENT (Staff & Admin)
# ─────────────────────────────────────────────────────────────────────────────

@router.get(
    "/knowledge",
    response_model=List[KnowledgeEntryResponse],
    summary="Get all DGDA Agent IA RAG knowledge training entries",
)
async def get_knowledge_entries(
    current_user: User = Depends(get_current_active_staff),
):
    """Retrieves all domain training items loaded into Agent IA reasoning engine."""
    return AIChatService.get_all_knowledge_entries()


@router.post(
    "/knowledge",
    response_model=KnowledgeEntryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new custom Q&A pair to Agent IA RAG knowledge base",
)
async def add_knowledge_entry(
    payload: KnowledgeEntryCreate,
    current_user: User = Depends(get_current_active_staff),
):
    """Inserts a new Q&A domain knowledge entry into Agent IA training set."""
    created = AIChatService.add_knowledge_entry(payload.dict())
    return created


@router.put(
    "/knowledge/{entry_id}",
    response_model=KnowledgeEntryResponse,
    summary="Update an existing Q&A pair in Agent IA knowledge base",
)
async def update_knowledge_entry(
    entry_id: str,
    payload: KnowledgeEntryUpdate,
    current_user: User = Depends(get_current_active_staff),
):
    """Updates question, category, answer, or legal reference for an entry."""
    updated = AIChatService.update_knowledge_entry(entry_id, payload.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge entry '{entry_id}' not found",
        )
    return updated


@router.delete(
    "/knowledge/{entry_id}",
    summary="Delete a Q&A pair from Agent IA knowledge base",
)
async def delete_knowledge_entry(
    entry_id: str,
    current_user: User = Depends(get_current_active_staff),
):
    """Removes an entry from the knowledge base."""
    success = AIChatService.delete_knowledge_entry(entry_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge entry '{entry_id}' not found",
        )
    return {"success": True, "message": f"Knowledge entry '{entry_id}' removed successfully"}


@router.post(
    "/knowledge/{entry_id}/recalibrate",
    response_model=KnowledgeEntryResponse,
    summary="Recalibrate and boost confidence weights for an entry",
)
async def recalibrate_knowledge_entry(
    entry_id: str,
    current_user: User = Depends(get_current_active_staff),
):
    """Increases confidence and recalculates vector weighting."""
    recalibrated = AIChatService.recalibrate_entry(entry_id)
    if not recalibrated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge entry '{entry_id}' not found",
        )
    return recalibrated


@router.post(
    "/test",
    response_model=TestAgentQueryResponse,
    summary="Live test Agent IA response in admin test console",
)
async def test_agent_query(
    payload: TestAgentQueryRequest,
    current_user: User = Depends(get_current_active_staff),
):
    """Tests an inquiry directly against the customs reasoning engine without persisting to user history."""
    result = AIChatService._fallback_knowledge_response(payload.query)
    return TestAgentQueryResponse(
        query=payload.query,
        reply=result.get("reply", ""),
        category=result.get("category", "General Inquiries"),
        legal_reference=result.get("legal_reference"),
        legalReference=result.get("legal_reference"),
        officialAnswer=result.get("reply", ""),
        confidence=result.get("confidence", 90),
        matched_id=result.get("matched_id"),
    )
