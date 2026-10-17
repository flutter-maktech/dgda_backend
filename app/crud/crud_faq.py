import asyncio
import json
import os
import uuid
from typing import List, Optional
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.faq import FAQ
from app.schemas.faq import FAQCreate, FAQUpdate

_faq_seed_lock = asyncio.Lock()
SEEDS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "seeds")


class CRUDFAQ:
    async def get_all_faqs(
        self,
        db: AsyncSession,
        status: Optional[str] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[FAQ]:
        await self.seed_faqs_if_empty(db)
        stmt = select(FAQ).order_by(FAQ.no.asc(), FAQ.created_at.asc())

        if status and status.upper() != "ALL":
            stmt = stmt.where(FAQ.status.ilike(status))
        if category and category.lower() != "all":
            stmt = stmt.where(FAQ.category.ilike(category))
        if search:
            pattern = f"%{search.lower()}%"
            stmt = stmt.where(
                FAQ.question.ilike(pattern)
                | FAQ.answer.ilike(pattern)
                | FAQ.category.ilike(pattern)
            )

        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_faq_by_id(self, db: AsyncSession, faq_id: str) -> Optional[FAQ]:
        stmt = select(FAQ).where(FAQ.id == faq_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def create_faq(self, db: AsyncSession, obj_in: FAQCreate) -> FAQ:
        data = obj_in.model_dump()
        if not data.get("id"):
            data["id"] = f"faq-{uuid.uuid4().hex[:8]}"

        # Calculate next number if not provided
        if not data.get("no"):
            count_stmt = select(func.count()).select_from(FAQ)
            res = await db.execute(count_stmt)
            data["no"] = (res.scalar() or 0) + 1

        db_obj = FAQ(**data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_faq(
        self, db: AsyncSession, db_obj: FAQ, obj_in: FAQUpdate
    ) -> FAQ:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete_faq(self, db: AsyncSession, faq_id: str) -> bool:
        db_obj = await self.get_faq_by_id(db, faq_id)
        if not db_obj:
            return False
        await db.delete(db_obj)
        await db.commit()
        return True

    async def seed_faqs_if_empty(self, db: AsyncSession) -> None:
        async with _faq_seed_lock:
            try:
                count_stmt = select(func.count()).select_from(FAQ)
                res = await db.execute(count_stmt)
                total_count = res.scalar() or 0

                if total_count >= 5:
                    return

                json_path = os.path.join(SEEDS_DIR, "faqs.json")
                if os.path.exists(json_path):
                    with open(json_path, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    if total_count > 0:
                        await db.execute(text("DELETE FROM faqs"))
                        await db.commit()

                    for item in data:
                        db.add(FAQ(**item))
                    await db.commit()
                    print(f"Seeded {len(data)} DGDA FAQs successfully.")
            except Exception as e:
                await db.rollback()
                print(f"Error seeding FAQs from JSON: {e}")


crud_faq = CRUDFAQ()
