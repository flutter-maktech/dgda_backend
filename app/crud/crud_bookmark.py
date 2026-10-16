from typing import List, Dict
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user_bookmark import UserBookmark


class CRUDBookmark:
    async def get_user_bookmark_ids(self, db: AsyncSession, user_id: int) -> Dict[str, List[str]]:
        stmt = select(UserBookmark).where(UserBookmark.user_id == user_id)
        result = await db.execute(stmt)
        bookmarks = result.scalars().all()

        news_ids = [b.item_id for b in bookmarks if b.item_type == "news"]
        document_ids = [b.item_id for b in bookmarks if b.item_type in ("document", "documents")]
        office_ids = [b.item_id for b in bookmarks if b.item_type in ("office", "offices")]

        return {
            "news": news_ids,
            "documents": document_ids,
            "offices": office_ids,
        }

    async def get_ids_by_type(self, db: AsyncSession, user_id: int, item_type: str) -> List[str]:
        # Normalize
        normalized_type = item_type.rstrip("s").lower()
        stmt = select(UserBookmark.item_id).where(
            UserBookmark.user_id == user_id,
            (UserBookmark.item_type == normalized_type) | (UserBookmark.item_type == item_type)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def toggle(
        self,
        db: AsyncSession,
        user_id: int,
        item_type: str,
        item_id: str
    ) -> bool:
        normalized_type = item_type.rstrip("s").lower()
        
        # Check if already exists
        stmt = select(UserBookmark).where(
            UserBookmark.user_id == user_id,
            UserBookmark.item_type == normalized_type,
            UserBookmark.item_id == str(item_id),
        )
        result = await db.execute(stmt)
        existing = result.scalars().first()

        if existing:
            await db.delete(existing)
            await db.commit()
            return False
        else:
            new_bookmark = UserBookmark(
                user_id=user_id,
                item_type=normalized_type,
                item_id=str(item_id),
            )
            db.add(new_bookmark)
            await db.commit()
            return True


crud_bookmark = CRUDBookmark()
