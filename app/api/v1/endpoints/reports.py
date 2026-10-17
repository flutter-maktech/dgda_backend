from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_admin, get_current_user_optional, get_db
from app.crud.crud_report import crud_report
from app.models.user import User
from app.schemas.incorrect_data_report import (
    ReportCreate,
    ReportResponse,
    ReportUpdate,
)

router = APIRouter()


@router.get("", response_model=List[ReportResponse])
@router.get("/", response_model=List[ReportResponse], include_in_schema=False)
async def get_reports(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (PENDING, UNDER_REVIEW, RESOLVED, ALL)"),
    search: Optional[str] = Query(None, description="Search term in code, reporter, description"),
    db: AsyncSession = Depends(get_db),
):
    """
    Récupère la liste des signalements d'anomalies et données incorrectes.
    Accessible pour le tableau de bord d'administration et la consultation mobile.
    """
    reports = await crud_report.get_all_reports(
        db=db,
        status=status_filter,
        search=search,
    )
    return reports


@router.get("/{id}", response_model=ReportResponse)
async def get_report(
    id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Récupère les détails complets d'un signalement d'anomalie.
    """
    report = await crud_report.get_report_by_id(db, report_id=id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Signalement non trouvé",
        )
    return report


@router.post(
    "",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
)
@router.post(
    "/",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def create_report(
    payload: ReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Soumet un nouveau signalement de données incorrectes ou anomalie douanière.
    Ouvert aux usagers de l'application mobile (authentifiés ou anonymes).
    """
    new_report = await crud_report.create_report(
        db=db,
        obj_in=payload,
        user=current_user,
    )
    return new_report


@router.put("/{id}", response_model=ReportResponse)
async def update_report(
    id: str,
    payload: ReportUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin),
):
    """
    Met à jour le statut ou les notes d'audit d'un signalement (Admin uniquement).
    """
    report = await crud_report.get_report_by_id(db, report_id=id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Signalement non trouvé",
        )
    updated = await crud_report.update_report(db, db_obj=report, obj_in=payload)
    return updated


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin),
):
    """
    Supprime un rapport d'anomalie (Admin uniquement).
    """
    success = await crud_report.delete_report(db, report_id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Signalement non trouvé",
        )
    return None
