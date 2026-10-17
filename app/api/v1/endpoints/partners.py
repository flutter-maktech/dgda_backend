from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_admin, get_db
from app.crud.crud_partner import crud_partner
from app.models.user import User
from app.schemas.partner import (
    PartnerCreate,
    PartnerResponse,
    PartnerUpdate,
)

router = APIRouter()


@router.get("", response_model=List[PartnerResponse])
async def get_partners(
    category: Optional[str] = Query(None, description="Category filter (Partners, Sponsors, Logistics, Banking, Insurance, etc.)"),
    is_partner: Optional[bool] = Query(None, description="True for Partners/Sponsors, False for Recommended Professionals"),
    is_principal_sponsor: Optional[bool] = Query(None, description="Filter for Principal Sponsor"),
    status_filter: Optional[str] = Query(None, alias="status", description="Status filter (Active, Inactive)"),
    search: Optional[str] = Query(None, description="Search term across name, role, category, tagline"),
    db: AsyncSession = Depends(get_db),
):
    """
    Récupère la liste des Partenaires, Sponsors et Professionnels recommandés de la DGDA.
    Accessible publiquement pour l'application mobile et le dashboard d'administration.
    """
    partners = await crud_partner.get_all_partners(
        db=db,
        category=category,
        is_partner=is_partner,
        is_principal_sponsor=is_principal_sponsor,
        status=status_filter,
        search=search,
    )
    return partners


@router.get("/principal-sponsor", response_model=Optional[PartnerResponse])
async def get_principal_sponsor(
    db: AsyncSession = Depends(get_db),
):
    """
    Récupère le sponsor principal officiel de la DGDA (UGP-MOD).
    """
    partners = await crud_partner.get_all_partners(
        db=db,
        is_principal_sponsor=True,
        status="Active",
    )
    if partners:
        return partners[0]
    return None


@router.get("/{id}", response_model=PartnerResponse)
async def get_partner(
    id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Récupère le profil détaillé d'un partenaire, sponsor ou professionnel recommandé.
    """
    partner = await crud_partner.get_partner_by_id(db, partner_id=id)
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partenaire non trouvé",
        )
    return partner


@router.post(
    "",
    response_model=PartnerResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_partner(
    payload: PartnerCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin),
):
    """
    Crée un nouveau partenaire, sponsor ou professionnel recommandé (Admin uniquement).
    """
    new_partner = await crud_partner.create_partner(db, obj_in=payload)
    return new_partner


@router.put("/{id}", response_model=PartnerResponse)
async def update_partner(
    id: str,
    payload: PartnerUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin),
):
    """
    Met à jour un partenaire ou professionnel existant (Admin uniquement).
    """
    partner = await crud_partner.get_partner_by_id(db, partner_id=id)
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partenaire non trouvé",
        )
    updated = await crud_partner.update_partner(db, db_obj=partner, obj_in=payload)
    return updated


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_partner(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin),
):
    """
    Supprime un partenaire ou professionnel (Admin uniquement).
    """
    success = await crud_partner.delete_partner(db, partner_id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partenaire non trouvé",
        )
    return None
