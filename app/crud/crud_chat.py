from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.chat_message import ChatMessage


INITIAL_WELCOME_MESSAGE = (
    "Bonjour et bienvenue sur l'assistant officiel de la Direction Générale des Douanes et Accises (DGDA). "
    "Comment puis-je vous aider aujourd'hui dans vos formalités douanières, calculs de droits ou procédures d'import/export ?"
)


async def get_chat_history(db: AsyncSession, user_id: int) -> List[ChatMessage]:
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.user_id == user_id)
        .order_by(ChatMessage.created_at.asc())
    )
    messages = list(result.scalars().all())

    # If empty, seed initial welcome greeting from Agent IA
    if not messages:
        welcome = ChatMessage(
            user_id=user_id,
            role="assistant",
            content=INITIAL_WELCOME_MESSAGE,
            legal_reference="Direction Générale des Douanes et Accises (DGDA RDC)",
            category="Customs Clearance"
        )
        db.add(welcome)
        await db.commit()
        await db.refresh(welcome)
        messages = [welcome]

    return messages


async def save_chat_message(
    db: AsyncSession,
    user_id: int,
    role: str,
    content: str,
    legal_reference: Optional[str] = None,
    category: Optional[str] = None
) -> ChatMessage:
    msg = ChatMessage(
        user_id=user_id,
        role=role,
        content=content,
        legal_reference=legal_reference,
        category=category
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg


async def clear_chat_history(db: AsyncSession, user_id: int) -> bool:
    await db.execute(
        delete(ChatMessage).where(ChatMessage.user_id == user_id)
    )
    await db.commit()
    return True
