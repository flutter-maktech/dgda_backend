from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_admin, get_db
from app.crud.crud_official import crud_official
from app.models.user import User
from app.schemas.official import (
    GovernmentOfficialCreate,
    GovernmentOfficialResponse,
    GovernmentOfficialUpdate,
    ManagementMemberCreate,
    ManagementMemberResponse,
    ManagementMemberUpdate,
)

router = APIRouter()


# ==========================================
# 1. GOVERNMENT OFFICIALS (Présidence & Gouv)
# ==========================================

@router.get("/government", response_model=List[GovernmentOfficialResponse])
async def get_government_officials(
    db: AsyncSession = Depends(get_db),
):
    """
    Récupère la liste officielle des dirigeants de la République (Présidence & Gouvernement).
    Accessible publiquement pour l'application mobile et le portail web.
    """
    officials = await crud_official.get_all_government_officials(db)
    return officials


@router.get("/government/{id}", response_model=GovernmentOfficialResponse)
async def get_government_official(
    id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Récupère le profil détaillé d'un dirigeant de la Présidence ou du Gouvernement.
    """
    official = await crud_official.get_government_official_by_id(db, official_id=id)
    if not official:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dirigeant non trouvé",
        )
    return official


@router.post(
    "/government",
    response_model=GovernmentOfficialResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_government_official(
    payload: GovernmentOfficialCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin),
):
    """
    Ajoute un nouveau dirigeant (Réservé aux Administrateurs).
    Utilisé par le futur tableau de bord d'administration (Admin Dashboard).
    """
    existing = await crud_official.get_government_official_by_id(db, official_id=payload.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un dirigeant avec cet identifiant existe déjà",
        )
    created = await crud_official.create_government_official(db, obj_in=payload)
    return created


@router.patch("/government/{id}", response_model=GovernmentOfficialResponse)
async def update_government_official(
    id: str,
    payload: GovernmentOfficialUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin),
):
    """
    Modifie les informations d'un dirigeant (Réservé aux Administrateurs).
    """
    official = await crud_official.get_government_official_by_id(db, official_id=id)
    if not official:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dirigeant non trouvé",
        )
    updated = await crud_official.update_government_official(
        db, db_obj=official, obj_in=payload
    )
    return updated


@router.delete("/government/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_government_official(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin),
):
    """
    Supprime un dirigeant de la liste officielle (Réservé aux Administrateurs).
    """
    deleted = await crud_official.delete_government_official(db, official_id=id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dirigeant non trouvé",
        )
    return None


# ==========================================
# 2. MANAGEMENT MEMBERS (Direction DGDA)
# ==========================================

@router.get("/management", response_model=List[ManagementMemberResponse])
async def get_management_members(
    category: Optional[str] = Query(
        None,
        description="Catégorie (directionGenerale, directeursCentraux, directeursProvinciaux, representantsEtranger, delegationSyndicale)",
    ),
    filter_tag: Optional[str] = Query(None, description="Tag de filtre secondaire"),
    search: Optional[str] = Query(None, description="Recherche par nom, poste, département ou ville"),
    db: AsyncSession = Depends(get_db),
):
    """
    Récupère la liste des cadres et responsables de la DGDA.
    Accessible publiquement avec support des filtres par catégorie et recherche.
    """
    members = await crud_official.get_all_management_members(
        db, category=category, filter_tag=filter_tag, search=search
    )
    return members


@router.get("/management/{id}", response_model=ManagementMemberResponse)
async def get_management_member(
    id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Récupère le profil complet d'un responsable de la DGDA.
    """
    member = await crud_official.get_management_member_by_id(db, member_id=id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Responsable non trouvé",
        )
    return member


@router.post(
    "/management",
    response_model=ManagementMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_management_member(
    payload: ManagementMemberCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin),
):
    """
    Ajoute un nouveau responsable à l'organigramme DGDA (Réservé aux Administrateurs).
    Utilisé par le futur tableau de bord d'administration (Admin Dashboard).
    """
    existing = await crud_official.get_management_member_by_id(db, member_id=payload.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un responsable avec cet identifiant existe déjà",
        )
    created = await crud_official.create_management_member(db, obj_in=payload)
    return created


@router.patch("/management/{id}", response_model=ManagementMemberResponse)
async def update_management_member(
    id: str,
    payload: ManagementMemberUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin),
):
    """
    Modifie les informations d'un responsable DGDA (Réservé aux Administrateurs).
    """
    member = await crud_official.get_management_member_by_id(db, member_id=id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Responsable non trouvé",
        )
    updated = await crud_official.update_management_member(
        db, db_obj=member, obj_in=payload
    )
    return updated


@router.delete("/management/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_management_member(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin),
):
    """
    Supprime un responsable de l'organigramme DGDA (Réservé aux Administrateurs).
    """
    deleted = await crud_official.delete_management_member(db, member_id=id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Responsable non trouvé",
        )
    return None
