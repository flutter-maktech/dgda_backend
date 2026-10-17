import asyncio
import json
import os
from typing import List, Optional
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content_document import ContentDocument
from app.schemas.content_document import ContentDocumentCreate, ContentDocumentUpdate

_content_seed_lock = asyncio.Lock()
SEEDS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "seeds")


class CRUDContent:
    async def get_by_type(
        self, db: AsyncSession, doc_type: str
    ) -> Optional[ContentDocument]:
        await self.seed_content_if_empty(db)
        # Normalize type (e.g. privacy_policy -> privacy-policy)
        normalized = doc_type.replace("_", "-").lower()
        stmt = select(ContentDocument).where(ContentDocument.type == normalized)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_by_id(
        self, db: AsyncSession, doc_id: str
    ) -> Optional[ContentDocument]:
        await self.seed_content_if_empty(db)
        stmt = select(ContentDocument).where(
            (ContentDocument.id == doc_id) | (ContentDocument.type == doc_id.replace("_", "-").lower())
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_all(self, db: AsyncSession) -> List[ContentDocument]:
        await self.seed_content_if_empty(db)
        stmt = select(ContentDocument).order_by(ContentDocument.created_at.asc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def create_or_update_by_type(
        self,
        db: AsyncSession,
        doc_type: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        card_title: Optional[str] = None,
        hero_title: Optional[str] = None,
        subtitle: Optional[str] = None,
        paragraphs: Optional[List[str]] = None,
    ) -> ContentDocument:
        doc = await self.get_by_type(db, doc_type)
        if not doc:
            doc = ContentDocument(
                id=f"doc-{doc_type.replace('_', '-').lower()}",
                type=doc_type.replace("_", "-").lower(),
                title=title or doc_type.capitalize(),
                card_title=card_title or title or doc_type.capitalize(),
                hero_title=hero_title or title or doc_type.capitalize(),
                subtitle=subtitle or "",
                content=content or "",
                paragraphs=paragraphs or [],
            )
            db.add(doc)
        else:
            if title is not None:
                doc.title = title
            if content is not None:
                doc.content = content
            if card_title is not None:
                doc.card_title = card_title
            if hero_title is not None:
                doc.hero_title = hero_title
            if subtitle is not None:
                doc.subtitle = subtitle
            if paragraphs is not None:
                doc.paragraphs = paragraphs
            db.add(doc)

        await db.commit()
        await db.refresh(doc)
        return doc

    async def update(
        self, db: AsyncSession, db_obj: ContentDocument, obj_in: ContentDocumentUpdate
    ) -> ContentDocument:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def seed_content_if_empty(self, db: AsyncSession) -> None:
        async with _content_seed_lock:
            try:
                count_stmt = select(func.count()).select_from(ContentDocument)
                res = await db.execute(count_stmt)
                total_count = res.scalar() or 0

                if total_count >= 3:
                    return

                json_path = os.path.join(SEEDS_DIR, "content_documents.json")
                if os.path.exists(json_path):
                    with open(json_path, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    if total_count > 0:
                        await db.execute(text("DELETE FROM content_documents"))
                        await db.commit()

                    for item in data:
                        db.add(ContentDocument(**item))
                    await db.commit()
                    print(f"Seeded {len(data)} Content Documents (Privacy Policy, Terms, About) successfully.")
            except Exception as e:
                await db.rollback()
                print(f"Error seeding Content Documents: {e}")


crud_content = CRUDContent()
