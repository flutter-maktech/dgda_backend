import asyncio
import json
import os
from typing import List, Optional
from sqlalchemy import select, text, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.official import GovernmentOfficial, ManagementMember
from app.schemas.official import (
    GovernmentOfficialCreate,
    GovernmentOfficialUpdate,
    ManagementMemberCreate,
    ManagementMemberUpdate,
)

_official_seed_lock = asyncio.Lock()
SEEDS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "seeds")


class CRUDOfficial:
    # ==========================================
    # 1. GOVERNMENT OFFICIALS (Présidence & Gouv)
    # ==========================================
    async def get_all_government_officials(
        self, db: AsyncSession
    ) -> List[GovernmentOfficial]:
        await self.seed_government_officials_if_empty(db)
        stmt = (
            select(GovernmentOfficial)
            .order_by(GovernmentOfficial.display_order.asc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_government_official_by_id(
        self, db: AsyncSession, official_id: str
    ) -> Optional[GovernmentOfficial]:
        stmt = select(GovernmentOfficial).where(GovernmentOfficial.id == official_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def create_government_official(
        self, db: AsyncSession, obj_in: GovernmentOfficialCreate
    ) -> GovernmentOfficial:
        db_obj = GovernmentOfficial(**obj_in.model_dump())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_government_official(
        self, db: AsyncSession, db_obj: GovernmentOfficial, obj_in: GovernmentOfficialUpdate
    ) -> GovernmentOfficial:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete_government_official(
        self, db: AsyncSession, official_id: str
    ) -> bool:
        db_obj = await self.get_government_official_by_id(db, official_id)
        if not db_obj:
            return False
        await db.delete(db_obj)
        await db.commit()
        return True

    # ==========================================
    # 2. MANAGEMENT MEMBERS (Direction DGDA)
    # ==========================================
    async def get_all_management_members(
        self,
        db: AsyncSession,
        category: Optional[str] = None,
        filter_tag: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[ManagementMember]:
        await self.seed_management_members_if_empty(db)
        stmt = select(ManagementMember).order_by(ManagementMember.display_order.asc())

        if category:
            stmt = stmt.where(ManagementMember.category == category)
        if filter_tag and filter_tag.lower() != "all" and filter_tag.lower() != "tous":
            stmt = stmt.where(ManagementMember.filter_tag == filter_tag)
        if search:
            pattern = f"%{search.lower()}%"
            stmt = stmt.where(
                ManagementMember.full_name.ilike(pattern)
                | ManagementMember.role_or_title.ilike(pattern)
                | ManagementMember.department.ilike(pattern)
                | ManagementMember.location.ilike(pattern)
            )

        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_management_member_by_id(
        self, db: AsyncSession, member_id: str
    ) -> Optional[ManagementMember]:
        stmt = select(ManagementMember).where(ManagementMember.id == member_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def create_management_member(
        self, db: AsyncSession, obj_in: ManagementMemberCreate
    ) -> ManagementMember:
        db_obj = ManagementMember(**obj_in.model_dump())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_management_member(
        self, db: AsyncSession, db_obj: ManagementMember, obj_in: ManagementMemberUpdate
    ) -> ManagementMember:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete_management_member(
        self, db: AsyncSession, member_id: str
    ) -> bool:
        db_obj = await self.get_management_member_by_id(db, member_id)
        if not db_obj:
            return False
        await db.delete(db_obj)
        await db.commit()
        return True

    # ==========================================
    # 3. AUTO-SEEDING ROUTINES (Loads from JSON Seeds)
    # ==========================================
    async def seed_government_officials_if_empty(self, db: AsyncSession) -> None:
        async with _official_seed_lock:
            try:
                stmt = select(GovernmentOfficial).limit(1)
                res = await db.execute(stmt)
                if res.scalars().first() is not None:
                    return

                json_path = os.path.join(SEEDS_DIR, "government_officials.json")
                if os.path.exists(json_path):
                    with open(json_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    for item in data:
                        db.add(GovernmentOfficial(**item))
                    await db.commit()
            except Exception as e:
                await db.rollback()
                print(f"Error seeding government officials from JSON: {e}")

    async def seed_management_members_if_empty(self, db: AsyncSession) -> None:
        async with _official_seed_lock:
            try:
                count_stmt = select(func.count()).select_from(ManagementMember)
                res = await db.execute(count_stmt)
                total_count = res.scalar() or 0

                has_cloudinary_stmt = select(ManagementMember).where(
                    ManagementMember.photo_url.like("https://res.cloudinary.com/%")
                ).limit(1)
                res_cloud = await db.execute(has_cloudinary_stmt)
                has_cloudinary = res_cloud.scalars().first() is not None

                if total_count >= 50 and has_cloudinary:
                    return

                if total_count > 0:
                    await db.execute(text("DELETE FROM management_members"))
                    await db.commit()

                json_path = os.path.join(SEEDS_DIR, "management_members.json")
                if os.path.exists(json_path):
                    with open(json_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    for item in data:
                        db.add(ManagementMember(**item))
                    await db.commit()
            except Exception as e:
                await db.rollback()
                print(f"Error seeding management members from JSON: {e}")


crud_official = CRUDOfficial()
