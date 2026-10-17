import asyncio
import json
import os
import uuid
from typing import List, Optional
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.partner import Partner
from app.schemas.partner import PartnerCreate, PartnerUpdate

_partner_seed_lock = asyncio.Lock()
SEEDS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "seeds")


class CRUDPartner:
    async def get_all_partners(
        self,
        db: AsyncSession,
        category: Optional[str] = None,
        is_partner: Optional[bool] = None,
        is_principal_sponsor: Optional[bool] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Partner]:
        await self.seed_partners_if_empty(db)
        stmt = select(Partner).order_by(Partner.display_order.asc(), Partner.created_at.desc())

        if category and category.lower() != "all":
            stmt = stmt.where(Partner.category.ilike(category))
        if is_partner is not None:
            stmt = stmt.where(Partner.is_partner == is_partner)
        if is_principal_sponsor is not None:
            stmt = stmt.where(Partner.is_principal_sponsor == is_principal_sponsor)
        elif is_partner is True:
            # By default exclude principal sponsor from standard partners/sponsors carousel
            stmt = stmt.where(Partner.is_principal_sponsor == False)
        if status:
            stmt = stmt.where(Partner.status.ilike(status))
        if search:
            pattern = f"%{search.lower()}%"
            stmt = stmt.where(
                Partner.name.ilike(pattern)
                | Partner.role.ilike(pattern)
                | Partner.category.ilike(pattern)
                | Partner.tagline.ilike(pattern)
            )

        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_partner_by_id(
        self, db: AsyncSession, partner_id: str
    ) -> Optional[Partner]:
        stmt = select(Partner).where(Partner.id == partner_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def create_partner(
        self, db: AsyncSession, obj_in: PartnerCreate
    ) -> Partner:
        data = obj_in.model_dump()
        if not data.get("id"):
            data["id"] = f"partner-{uuid.uuid4().hex[:8]}"
        db_obj = Partner(**data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_partner(
        self, db: AsyncSession, db_obj: Partner, obj_in: PartnerUpdate
    ) -> Partner:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete_partner(
        self, db: AsyncSession, partner_id: str
    ) -> bool:
        db_obj = await self.get_partner_by_id(db, partner_id)
        if not db_obj:
            return False
        await db.delete(db_obj)
        await db.commit()
        return True

    async def seed_partners_if_empty(self, db: AsyncSession) -> None:
        async with _partner_seed_lock:
            try:
                count_stmt = select(func.count()).select_from(Partner)
                res = await db.execute(count_stmt)
                total_count = res.scalar() or 0

                if total_count >= 10:
                    return

                json_path = os.path.join(SEEDS_DIR, "partners.json")
                if os.path.exists(json_path):
                    with open(json_path, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    if total_count > 0:
                        await db.execute(text("DELETE FROM partners"))
                        await db.commit()

                    for item in data:
                        db.add(Partner(**item))
                    await db.commit()
                    print(f"Seeded {len(data)} partners, sponsors and professionals successfully.")
            except Exception as e:
                await db.rollback()
                print(f"Error seeding partners from JSON: {e}")


crud_partner = CRUDPartner()
