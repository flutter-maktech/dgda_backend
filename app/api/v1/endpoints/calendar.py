from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.crud.crud_calendar_event import (
    create_calendar_event,
    delete_calendar_event,
    get_calendar_event_by_id,
    get_user_calendar_events,
    update_calendar_event,
)
from app.models.user import User
from app.schemas.calendar_event import (
    CalendarEventCreate,
    CalendarEventResponse,
    CalendarEventUpdate,
)

router = APIRouter()


@router.get(
    "/events",
    response_model=List[CalendarEventResponse],
    summary="List all customs calendar events for current user"
)
async def list_calendar_events(
    month: Optional[str] = Query(None, description="Filter by year-month (e.g. 2026-10)"),
    date: Optional[str] = Query(None, description="Filter by specific date (e.g. 2026-10-16)"),
    status: Optional[str] = Query(None, description="Filter by status: scheduled, completed, cancelled, all"),
    search: Optional[str] = Query(None, description="Search term in title, location, reference or description"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve customs calendar events belonging to the authenticated user.
    """
    events = await get_user_calendar_events(
        db,
        user_id=current_user.id,
        month=month,
        date=date,
        status=status,
        search=search,
    )
    return [CalendarEventResponse.from_orm_custom(e) for e in events]


@router.post(
    "/events",
    response_model=CalendarEventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new customs calendar event"
)
async def create_new_calendar_event(
    event_in: CalendarEventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Schedule a new customs calendar event (inspection, meeting, audit, clearance).
    """
    created = await create_calendar_event(
        db, event_in=event_in, user_id=current_user.id
    )
    return CalendarEventResponse.from_orm_custom(created)


@router.get(
    "/events/{event_id}",
    response_model=CalendarEventResponse,
    summary="Get single calendar event details"
)
async def get_single_calendar_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get full details of a specific customs calendar event.
    """
    event = await get_calendar_event_by_id(db, event_id=event_id, user_id=current_user.id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar event not found"
        )
    return CalendarEventResponse.from_orm_custom(event)


@router.patch(
    "/events/{event_id}",
    response_model=CalendarEventResponse,
    summary="Update or reschedule a customs calendar event"
)
async def update_existing_calendar_event(
    event_id: int,
    event_in: CalendarEventUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update details, reschedule date/time, or mark event completed.
    """
    updated = await update_calendar_event(
        db, event_id=event_id, event_in=event_in, user_id=current_user.id
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar event not found or access denied"
        )
    return CalendarEventResponse.from_orm_custom(updated)


@router.delete(
    "/events/{event_id}",
    summary="Delete a customs calendar event"
)
async def delete_existing_calendar_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Cancel or delete an scheduled customs calendar event.
    """
    success = await delete_calendar_event(db, event_id=event_id, user_id=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar event not found or access denied"
        )
    return {"message": "Customs event deleted successfully", "id": event_id}
