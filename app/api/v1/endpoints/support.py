from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    get_current_active_admin,
    get_current_user_optional,
    get_db,
)
from app.crud.crud_support import crud_support
from app.models.user import User
from app.schemas.technical_support import (
    SupportTicketCreate,
    SupportTicketResponse,
    SupportTicketUpdate,
    TechnicalSupportInfoResponse,
    TechnicalSupportInfoUpdate,
)

router = APIRouter()


# =========================================================================
# Technical Support / 24/7 Helpdesk Information
# =========================================================================

@router.get("", response_model=TechnicalSupportInfoResponse)
@router.get("/", response_model=TechnicalSupportInfoResponse, include_in_schema=False)
@router.get("/info", response_model=TechnicalSupportInfoResponse, include_in_schema=False)
async def get_technical_support_info(db: AsyncSession = Depends(get_db)):
    """
    Récupère les coordonnées officielles de l'Assistance Technique DGDA 24h/24 et 7j/7.
    Accessible publiquement pour l'application mobile et le portail web.
    """
    info = await crud_support.get_support_info(db)
    return info


@router.put("", response_model=TechnicalSupportInfoResponse)
@router.put("/", response_model=TechnicalSupportInfoResponse, include_in_schema=False)
async def update_technical_support_info(
    payload: TechnicalSupportInfoUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin),
):
    """
    Met à jour les informations et coordonnées du support technique (Admin uniquement).
    """
    updated = await crud_support.update_support_info(db, obj_in=payload)
    return updated


# =========================================================================
# Support Tickets & Assistance Requests
# =========================================================================

@router.post(
    "/tickets",
    response_model=SupportTicketResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_support_ticket(
    payload: SupportTicketCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Soumet une nouvelle demande d'assistance technique ou un ticket helpdesk.
    Accessible aux usagers (connectés ou invités).
    """
    ticket = await crud_support.create_ticket(
        db=db,
        obj_in=payload,
        user=current_user,
    )
    return ticket


@router.get("/tickets", response_model=List[SupportTicketResponse])
async def get_support_tickets(
    status_filter: Optional[str] = Query(None, alias="status", description="Status filter (OPEN, IN_PROGRESS, RESOLVED, CLOSED, ALL)"),
    search: Optional[str] = Query(None, description="Search term in ticket number, name, subject"),
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin),
):
    """
    Consulte la liste des tickets d'assistance technique (Admin uniquement).
    """
    tickets = await crud_support.get_tickets(
        db=db,
        status=status_filter,
        search=search,
    )
    return tickets


@router.get("/tickets/{id}", response_model=SupportTicketResponse)
async def get_support_ticket(
    id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Récupère le détail d'un ticket d'assistance technique par son identifiant ou numéro.
    """
    ticket = await crud_support.get_ticket_by_id(db, ticket_id=id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket d'assistance introuvable",
        )
    return ticket


@router.put("/tickets/{id}", response_model=SupportTicketResponse)
async def update_support_ticket(
    id: str,
    payload: SupportTicketUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin),
):
    """
    Met à jour le statut, la priorité ou la réponse administrative à un ticket (Admin uniquement).
    """
    ticket = await crud_support.get_ticket_by_id(db, ticket_id=id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket d'assistance introuvable",
        )
    updated = await crud_support.update_ticket(db, db_obj=ticket, obj_in=payload)
    return updated
