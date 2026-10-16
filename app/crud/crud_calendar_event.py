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
    # Check if user has any events; if not, seed initial events
    count_stmt = select(CalendarEvent).where(CalendarEvent.user_id == user_id)
    count_res = await db.execute(count_stmt)
    if count_res.scalars().first() is None:
        await seed_user_initial_events(db, user_id)

    stmt = select(CalendarEvent).where(CalendarEvent.user_id == user_id)

    if month and month.strip():
        # E.g. "2026-10" or "10/2026"
        m = month.strip()
        stmt = stmt.where(CalendarEvent.event_date.contains(m))

    if date and date.strip():
        d = date.strip()
        stmt = stmt.where(CalendarEvent.event_date == d)

    if status and status.strip() and status.lower() != "all":
        stmt = stmt.where(CalendarEvent.status == status.strip())

    if search and search.strip():
        term = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                CalendarEvent.title.ilike(term),
                CalendarEvent.reference_code.ilike(term),
                CalendarEvent.location.ilike(term),
                CalendarEvent.category.ilike(term),
                CalendarEvent.description.ilike(term),
            )
        )

    stmt = stmt.order_by(CalendarEvent.event_date.asc(), CalendarEvent.time_slot.asc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create_calendar_event(
    db: AsyncSession,
    event_in: CalendarEventCreate,
    user_id: int,
) -> CalendarEvent:
    """Create a new customs calendar event."""
    ref = event_in.get_reference_code()
    if not ref:
        now = datetime.now()
        ref = f"REF: EVT/{now.year}/{now.strftime('%m%d%H%M')}"

    event = CalendarEvent(
        user_id=user_id,
        declaration_id=event_in.declaration_id,
        title=event_in.title.strip() if event_in.title else "Customs Event",
        category=event_in.category.strip() if event_in.category else "Forwarder Meeting",
        reference_code=ref.strip(),
        location=event_in.location.strip() if event_in.location else "Matadi Port Customs Office",
        event_date=event_in.get_event_date(),
        time_slot=event_in.get_time_slot(),
        reminder_date=event_in.get_reminder_date() or None,
        reminder_time=event_in.get_reminder_time() or None,
        description=event_in.description.strip() if event_in.description else None,
        status=event_in.status if event_in.status else "scheduled",
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


async def get_calendar_event_by_id(
    db: AsyncSession,
    event_id: int,
    user_id: Optional[int] = None,
) -> Optional[CalendarEvent]:
    """Retrieve a calendar event by ID, optionally verifying user ownership."""
    stmt = select(CalendarEvent).where(CalendarEvent.id == event_id)
    if user_id is not None:
        stmt = stmt.where(CalendarEvent.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalars().first()


async def update_calendar_event(
    db: AsyncSession,
    event_id: int,
    event_in: CalendarEventUpdate,
    user_id: Optional[int] = None,
) -> Optional[CalendarEvent]:
    """Update an existing calendar event."""
    event = await get_calendar_event_by_id(db, event_id=event_id, user_id=user_id)
    if not event:
        return None

    if event_in.title is not None:
        event.title = event_in.title.strip()
    if event_in.category is not None:
        event.category = event_in.category.strip()
    
    ref = event_in.reference_code or event_in.referenceCode
    if ref is not None:
        event.reference_code = ref.strip()

    if event_in.location is not None:
        event.location = event_in.location.strip()

    ev_date = event_in.event_date or event_in.eventDate or event_in.date
    if ev_date is not None:
        event.event_date = ev_date.strip()

    t_slot = event_in.time_slot or event_in.timeSlot or event_in.time
    if t_slot is not None:
        event.time_slot = t_slot.strip()

    rem_date = event_in.reminder_date or event_in.reminderDate
    if rem_date is not None:
        event.reminder_date = rem_date.strip()

    rem_time = event_in.reminder_time or event_in.reminderTime
    if rem_time is not None:
        event.reminder_time = rem_time.strip()

    if event_in.description is not None:
        event.description = event_in.description.strip()
    if event_in.status is not None:
        event.status = event_in.status.strip()
    if event_in.declaration_id is not None:
        event.declaration_id = event_in.declaration_id

    event.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(event)
    return event


async def delete_calendar_event(
    db: AsyncSession,
    event_id: int,
    user_id: Optional[int] = None,
) -> bool:
    """Delete a calendar event."""
    event = await get_calendar_event_by_id(db, event_id=event_id, user_id=user_id)
    if not event:
        return False

    await db.delete(event)
    await db.commit()
    return True
