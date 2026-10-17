import asyncio
import json
import os
import uuid
from typing import List, Optional
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.models.user_notification_read import UserNotificationRead
from app.schemas.notification import NotificationCreate, NotificationUpdate

_notif_seed_lock = asyncio.Lock()
SEEDS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "seeds")


class CRUDNotification:
    async def get_all_notifications(
        self,
        db: AsyncSession,
        category: Optional[str] = None,
        target_audience: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Notification]:
        await self.seed_notifications_if_empty(db)
        stmt = select(Notification).order_by(Notification.created_at.desc())

        if category and category.lower() != "all":
            stmt = stmt.where(Notification.category.ilike(category))
        if target_audience and target_audience.lower() != "all":
            stmt = stmt.where(Notification.target_audience.ilike(target_audience))
        if status and status.lower() != "all":
            stmt = stmt.where(Notification.status.ilike(status))
        if search:
            pattern = f"%{search.lower()}%"
            stmt = stmt.where(
                Notification.title.ilike(pattern)
                | Notification.subtitle.ilike(pattern)
                | Notification.body.ilike(pattern)
                | Notification.category.ilike(pattern)
            )

        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_notification_by_id(
        self, db: AsyncSession, notif_id: str
    ) -> Optional[Notification]:
        stmt = select(Notification).where(Notification.id == notif_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def create_notification(
        self, db: AsyncSession, obj_in: NotificationCreate
    ) -> Notification:
        data = obj_in.model_dump()
        if not data.get("id"):
            data["id"] = f"notif-{uuid.uuid4().hex[:8]}"

        db_obj = Notification(**data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_notification(
        self, db: AsyncSession, db_obj: Notification, obj_in: NotificationUpdate
    ) -> Notification:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete_notification(
        self, db: AsyncSession, notif_id: str
    ) -> bool:
        db_obj = await self.get_notification_by_id(db, notif_id)
        if not db_obj:
            return False
        await db.delete(db_obj)
        await db.commit()
        return True

    async def get_user_read_notification_ids(
        self, db: AsyncSession, user_id: int
    ) -> set[str]:
        stmt = select(UserNotificationRead.notification_id).where(
            UserNotificationRead.user_id == user_id
        )
        res = await db.execute(stmt)
        return set(res.scalars().all())

    async def mark_as_read(
        self, db: AsyncSession, user_id: int, notification_id: str
    ) -> bool:
        stmt = select(UserNotificationRead).where(
            UserNotificationRead.user_id == user_id,
            UserNotificationRead.notification_id == notification_id,
        )
        res = await db.execute(stmt)
        existing = res.scalars().first()
        if existing:
            return True

        read_record = UserNotificationRead(
            user_id=user_id,
            notification_id=notification_id,
        )
        db.add(read_record)
        await db.commit()
        return True

    async def mark_all_as_read(
        self, db: AsyncSession, user_id: int
    ) -> int:
        notif_stmt = select(Notification.id)
        res = await db.execute(notif_stmt)
        all_ids = res.scalars().all()

        existing_reads = await self.get_user_read_notification_ids(db, user_id)
        count = 0
        for nid in all_ids:
            if nid not in existing_reads:
                db.add(UserNotificationRead(user_id=user_id, notification_id=nid))
                count += 1
        if count > 0:
            await db.commit()
        return count

    async def seed_notifications_if_empty(self, db: AsyncSession) -> None:
        async with _notif_seed_lock:
            try:
                count_stmt = select(func.count()).select_from(Notification)
                res = await db.execute(count_stmt)
                total_count = res.scalar() or 0

                if total_count >= 5:
                    return

                json_path = os.path.join(SEEDS_DIR, "notifications.json")
                if os.path.exists(json_path):
                    with open(json_path, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    if total_count > 0:
                        await db.execute(text("DELETE FROM notifications"))
                        await db.commit()

                    for item in data:
                        db.add(Notification(**item))
                    await db.commit()
                    print(f"Seeded {len(data)} DGDA notifications successfully.")
            except Exception as e:
                await db.rollback()
                print(f"Error seeding notifications: {e}")


crud_notification = CRUDNotification()
