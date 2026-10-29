from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.calendar_event import CalendarEvent
from app.schemas.calendar_event import CalendarEventCreate, CalendarEventUpdate


def _get_seed_events_for_month() -> List[dict]:
    """Generates realistic DGDA calendar events anchored to the current month."""
    now = datetime.now()
    year_month = now.strftime("%Y-%m")
    
    return [
        {
            "title": "Physical Inspection & Contre-visite",
            "category": "Physical Inspection",
            "reference_code": "REF: IMP/2026/1258",
            "location": "Matadi Port Customs Office",
            "event_date": f"{year_month}-16",
            "time_slot": "10:00 AM",
            "reminder_date": f"{year_month}-15",
            "reminder_time": "09:00 AM",
            "description": "Physical inspection and valuation Clearance at Terminal 2, Port of Matadi.",
            "status": "scheduled",
        },
        {
            "title": "Forwarder Transit Meeting",
            "category": "Forwarder Meeting",
            "reference_code": "REF: TR/2026/2040",
            "location": "Kasumbalesa Border Post",
            "event_date": f"{year_month}-17",
            "time_slot": "02:30 PM",
            "reminder_date": f"{year_month}-16",
            "reminder_time": "01:00 PM",
            "description": "Coordination meeting with freight forwarders regarding SADC regional transit compliance.",
            "status": "scheduled",
        },
        {
            "title": "Valuation & Duty Clearance",
            "category": "Valuation Clearance",
            "reference_code": "REF: DEC/2026/0841",
            "location": "Kinshasa Aeroport Customs",
            "event_date": f"{year_month}-18",
            "time_slot": "11:00 AM",
            "reminder_date": f"{year_month}-17",
            "reminder_time": "10:00 AM",
            "description": "Duty payment validation and certificate of clearance issuance at N'djili cargo terminal.",
            "status": "scheduled",
        },
        {
            "title": "Customs Compliance Audit",
            "category": "Customs Audit",
            "reference_code": "REF: EXP/2026/0319",
            "location": "Goma Port Office",
            "event_date": f"{year_month}-23",
            "time_slot": "09:30 AM",
            "reminder_date": f"{year_month}-22",
            "reminder_time": "08:30 AM",
            "description": "Review of export origin certificates and mineral transport documentation.",
            "status": "scheduled",
        },
    ]


async def seed_user_initial_events(db: AsyncSession, user_id: int) -> None:
    """Seed initial realistic DGDA calendar events if user has none."""
    seed_data = _get_seed_events_for_month()
    for item in seed_data:
        event = CalendarEvent(
            user_id=user_id,
            title=item["title"],
            category=item["category"],
            reference_code=item["reference_code"],
            location=item["location"],
            event_date=item["event_date"],
            time_slot=item["time_slot"],
            reminder_date=item.get("reminder_date"),
            reminder_time=item.get("reminder_time"),
            description=item.get("description"),
            status=item["status"],
        )
        db.add(event)
    await db.commit()


async def get_user_calendar_events(
    db: AsyncSession,
    user_id: int,
    month: Optional[str] = None,
    date: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
) -> List[CalendarEvent]:
    """Retrieve calendar events for a user with optional month/date/status/search filters."""
    count_stmt = select(CalendarEvent).where(CalendarEvent.user_id == user_id)
    count_res = await db.execute(count_stmt)
    if count_res.scalars().first() is None:
        await seed_user_initial_events(db, user_id)

    stmt = select(CalendarEvent).where(CalendarEvent.user_id == user_id)

    if month and month.strip():
        stmt = stmt.where(CalendarEvent.event_date.contains(month.strip()))

    if date and date.strip():
        stmt = stmt.where(CalendarEvent.event_date == date.strip())

    if status and status.strip() and status.lower() != "all":
        stmt = stmt.where(CalendarEvent.status == status.strip())

    if search and search.strip():
        term = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                CalendarEvent.title.ilike(term),
                CalendarEvent.location.ilike(term),
                CalendarEvent.reference_code.ilike(term),
                CalendarEvent.category.ilike(term),
                CalendarEvent.description.ilike(term),
            )
        )

    stmt = stmt.order_by(CalendarEvent.event_date.asc(), CalendarEvent.time_slot.asc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_all_calendar_events(
    db: AsyncSession,
    month: Optional[str] = None,
    date: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
) -> List[CalendarEvent]:
    """Retrieve all calendar events across the entire DGDA administration."""
    count_stmt = select(CalendarEvent)
    count_res = await db.execute(count_stmt)
    if count_res.scalars().first() is None:
        await seed_user_initial_events(db, 1)

    stmt = select(CalendarEvent)

    if month and month.strip():
        stmt = stmt.where(CalendarEvent.event_date.contains(month.strip()))

    if date and date.strip():
        stmt = stmt.where(CalendarEvent.event_date == date.strip())

    if status and status.strip() and status.lower() != "all":
        stmt = stmt.where(CalendarEvent.status == status.strip())

    if search and search.strip():
        term = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                CalendarEvent.title.ilike(term),
                CalendarEvent.location.ilike(term),
                CalendarEvent.reference_code.ilike(term),
                CalendarEvent.category.ilike(term),
                CalendarEvent.description.ilike(term),
            )
        )

    stmt = stmt.order_by(CalendarEvent.event_date.asc(), CalendarEvent.time_slot.asc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_calendar_event_by_id(
    db: AsyncSession, event_id: int, user_id: Optional[int] = None
) -> Optional[CalendarEvent]:
    """Retrieve single event by primary key."""
    stmt = select(CalendarEvent).where(CalendarEvent.id == event_id)
    if user_id is not None:
        stmt = stmt.where(CalendarEvent.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalars().first()


async def create_calendar_event(
    db: AsyncSession, event_in: CalendarEventCreate, user_id: int
) -> CalendarEvent:
    """Create a new customs event."""
    ref_code = event_in.reference_code or event_in.referenceCode
    if not ref_code or not ref_code.strip():
        now = datetime.now()
        ref_code = f"REF: EVT/{now.year}/{random.randint(1000, 9999)}"

    event = CalendarEvent(
        user_id=user_id,
        title=event_in.title,
        category=event_in.category or "Customs Event",
        reference_code=ref_code,
        location=event_in.location or "DGDA Headquarters",
        event_date=event_in.get_event_date(),
        time_slot=event_in.get_time_slot(),
        reminder_date=event_in.get_reminder_date(),
        reminder_time=event_in.get_reminder_time(),
        description=event_in.description,
        status="scheduled",
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


async def update_calendar_event(
    db: AsyncSession, event_id: int, event_in: CalendarEventUpdate, user_id: Optional[int] = None
) -> Optional[CalendarEvent]:
    """Update details of a calendar event."""
    event = await get_calendar_event_by_id(db, event_id=event_id, user_id=user_id)
    if not event:
        return None

    raw_data = event_in.model_dump(exclude_unset=True)
    for field, value in raw_data.items():
        if hasattr(event, field) and value is not None:
            setattr(event, field, value)

    if "eventDate" in raw_data and raw_data["eventDate"]:
        event.event_date = raw_data["eventDate"]
    if "timeSlot" in raw_data and raw_data["timeSlot"]:
        event.time_slot = raw_data["timeSlot"]
    if "reminderDate" in raw_data:
        event.reminder_date = raw_data["reminderDate"]
    if "reminderTime" in raw_data:
        event.reminder_time = raw_data["reminderTime"]
    if "referenceCode" in raw_data and raw_data["referenceCode"]:
        event.reference_code = raw_data["referenceCode"]

    await db.commit()
    await db.refresh(event)
    return event


async def delete_calendar_event(
    db: AsyncSession, event_id: int, user_id: Optional[int] = None
) -> bool:
    """Delete or cancel a calendar event."""
    event = await get_calendar_event_by_id(db, event_id=event_id, user_id=user_id)
    if not event:
        return False
    await db.delete(event)
    await db.commit()
    return True
