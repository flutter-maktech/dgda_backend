import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.incorrect_data_report import IncorrectDataReport
from app.models.user import User
from app.schemas.incorrect_data_report import ReportCreate, ReportUpdate


class CRUDReport:
    async def get_all_reports(
        self,
        db: AsyncSession,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[IncorrectDataReport]:
        stmt = select(IncorrectDataReport).order_by(IncorrectDataReport.created_at.desc())

        if status and status.upper() != "ALL":
            stmt = stmt.where(IncorrectDataReport.status.ilike(status))
        if search:
            pattern = f"%{search.lower()}%"
            stmt = stmt.where(
                IncorrectDataReport.report_code.ilike(pattern)
                | IncorrectDataReport.reporting_user.ilike(pattern)
                | IncorrectDataReport.email.ilike(pattern)
                | IncorrectDataReport.description.ilike(pattern)
                | IncorrectDataReport.detailed_description.ilike(pattern)
            )

        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_report_by_id(
        self, db: AsyncSession, report_id: str
    ) -> Optional[IncorrectDataReport]:
        stmt = select(IncorrectDataReport).where(
            (IncorrectDataReport.id == report_id)
            | (IncorrectDataReport.report_code == report_id)
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def create_report(
        self,
        db: AsyncSession,
        obj_in: ReportCreate,
        user: Optional[User] = None,
    ) -> IncorrectDataReport:
        # Generate sequential report code: REP-YYYY-XXX
        year = datetime.now(timezone.utc).year
        count_stmt = select(func.count()).select_from(IncorrectDataReport)
        res = await db.execute(count_stmt)
        current_count = (res.scalar() or 0) + 1
        report_code = f"REP-{year}-{str(current_count).pad_zero if hasattr(str, 'pad_zero') else str(current_count).zfill(3)}"

        # Determine reporter details
        reporting_user = obj_in.reporting_user
        email = obj_in.email
        telephone = obj_in.telephone

        if user:
            if not reporting_user:
                reporting_user = user.full_name or user.username
            if not email:
                email = user.email
            if not telephone:
                telephone = user.phone_number or ""

        if not reporting_user:
            reporting_user = "Utilisateur DGDA"

        submission_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        db_obj = IncorrectDataReport(
            id=f"rep-{uuid.uuid4().hex[:8]}",
            report_code=report_code,
            reporting_user=reporting_user,
            email=email or "",
            telephone=telephone or "",
            description=obj_in.description or "Signalement de données erronées",
            detailed_description=obj_in.detailed_description,
            status="PENDING",
            admin_notes="",
            submission_date=submission_date,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_report(
        self,
        db: AsyncSession,
        db_obj: IncorrectDataReport,
        obj_in: ReportUpdate,
    ) -> IncorrectDataReport:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete_report(self, db: AsyncSession, report_id: str) -> bool:
        db_obj = await self.get_report_by_id(db, report_id)
        if not db_obj:
            return False
        await db.delete(db_obj)
        await db.commit()
        return True


crud_report = CRUDReport()
