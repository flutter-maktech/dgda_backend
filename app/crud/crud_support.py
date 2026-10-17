import asyncio
import json
import os
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.technical_support import TechnicalSupportInfo, SupportTicket
from app.models.user import User
from app.schemas.technical_support import (
    SupportTicketCreate,
    SupportTicketUpdate,
    TechnicalSupportInfoUpdate,
)

_support_seed_lock = asyncio.Lock()
SEEDS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "seeds")


class CRUDSupport:
    async def get_support_info(self, db: AsyncSession) -> TechnicalSupportInfo:
        await self.seed_support_info_if_empty(db)
        stmt = select(TechnicalSupportInfo).where(TechnicalSupportInfo.id == "dgda-helpdesk")
        result = await db.execute(stmt)
        info = result.scalars().first()
        if not info:
            # Fallback creation
            info = TechnicalSupportInfo(
                id="dgda-helpdesk",
                title="Assistance DGDA 24h/24 et 7j/7",
                description="Ligne directe pour les interruptions SydoniaWorld, les anomalies de scellés électroniques et les réconciliations de paiement SEGUCE.",
                phone_numbers="+243 81 700 0001 / +243 99 800 0002",
                phone_list=["+243817000001", "+243998000002"],
                email="support.sydonia@dgda.gouv.cd",
                whatsapp="+243821920215",
                portal_url="https://douane.gouv.cd/assistance",
                operating_hours="24/7 - Service Continu",
                is_active=True,
            )
            db.add(info)
            await db.commit()
            await db.refresh(info)
        return info

    async def update_support_info(
        self, db: AsyncSession, obj_in: TechnicalSupportInfoUpdate
    ) -> TechnicalSupportInfo:
        info = await self.get_support_info(db)
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(info, field, value)
        db.add(info)
        await db.commit()
        await db.refresh(info)
        return info

    async def create_ticket(
        self,
        db: AsyncSession,
        obj_in: SupportTicketCreate,
        user: Optional[User] = None,
    ) -> SupportTicket:
        year = datetime.now(timezone.utc).year
        count_stmt = select(func.count()).select_from(SupportTicket)
        res = await db.execute(count_stmt)
        current_count = (res.scalar() or 0) + 1
        ticket_number = f"SUP-{year}-{str(current_count).zfill(3)}"

        name = obj_in.name
        email = obj_in.email
        phone = obj_in.phone

        if user:
            if not name:
                name = user.full_name or user.username
            if not email:
                email = user.email
            if not phone:
                phone = user.phone_number or ""

        db_obj = SupportTicket(
            id=f"tkt-{uuid.uuid4().hex[:8]}",
            ticket_number=ticket_number,
            name=name or "Déclarant / Usager",
            email=email or "",
            phone=phone or "",
            subject=obj_in.subject,
            category=obj_in.category,
            message=obj_in.message,
            status="OPEN",
            priority="NORMAL",
            admin_notes="",
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_tickets(
        self,
        db: AsyncSession,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[SupportTicket]:
        stmt = select(SupportTicket).order_by(SupportTicket.created_at.desc())
        if status and status.upper() != "ALL":
            stmt = stmt.where(SupportTicket.status.ilike(status))
        if search:
            pattern = f"%{search.lower()}%"
            stmt = stmt.where(
                SupportTicket.ticket_number.ilike(pattern)
                | SupportTicket.name.ilike(pattern)
                | SupportTicket.subject.ilike(pattern)
                | SupportTicket.message.ilike(pattern)
            )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_ticket_by_id(
        self, db: AsyncSession, ticket_id: str
    ) -> Optional[SupportTicket]:
        stmt = select(SupportTicket).where(
            (SupportTicket.id == ticket_id) | (SupportTicket.ticket_number == ticket_id)
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def update_ticket(
        self, db: AsyncSession, db_obj: SupportTicket, obj_in: SupportTicketUpdate
    ) -> SupportTicket:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def seed_support_info_if_empty(self, db: AsyncSession) -> None:
        async with _support_seed_lock:
            try:
                count_stmt = select(func.count()).select_from(TechnicalSupportInfo)
                res = await db.execute(count_stmt)
                if (res.scalar() or 0) > 0:
                    return

                json_path = os.path.join(SEEDS_DIR, "support_info.json")
                if os.path.exists(json_path):
                    with open(json_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    db.add(TechnicalSupportInfo(**data))
                    await db.commit()
                    print("Seeded Technical Support Info successfully.")
            except Exception as e:
                await db.rollback()
                print(f"Error seeding Technical Support Info: {e}")


crud_support = CRUDSupport()
