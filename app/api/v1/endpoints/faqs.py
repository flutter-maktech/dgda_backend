from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_admin, get_db
from app.crud.crud_faq import crud_faq
from app.models.user import User
from app.schemas.faq import FAQCreate, FAQResponse, FAQUpdate

router = APIRouter()


@router.get("", response_model=List[FAQResponse])
@router.get("/", response_model=List[FAQResponse], include_in_schema=False)
async def get_faqs(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (ACTIVE, INACTIVE, or ALL)"),
    category: Optional[str] = Query(None, description="Category filter"),
    search: Optional[str] = Query(None, description="Search term in questions or answers"),
    db: AsyncSession = Depends(get_db),
):
    """
    Récupère la liste des questions fréquemment posées (FAQ) de la DGDA.
    Accessible publiquement pour l'application mobile et le portail web.
    """
    faqs = await crud_faq.get_all_faqs(
        db=db,
        status=status_filter,
        category=category,
        search=search,
    )
    return faqs


@router.get("/{id}", response_model=FAQResponse)
async def get_faq(
    id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Récupère le détail d'une question FAQ par son identifiant.
    """
    faq = await crud_faq.get_faq_by_id(db, faq_id=id)
    if not faq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FAQ non trouvée",
        )
    return faq


@router.post(
    "",
    response_model=FAQResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_faq(
    payload: FAQCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin),
):
    """
    Ajoute une nouvelle question à la FAQ (Admin uniquement).
    """
    new_faq = await crud_faq.create_faq(db, obj_in=payload)
    return new_faq


@router.put("/{id}", response_model=FAQResponse)
async def update_faq(
    id: str,
    payload: FAQUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin),
):
    """
    Met à jour une question de la FAQ (Admin uniquement).
    """
    faq = await crud_faq.get_faq_by_id(db, faq_id=id)
    if not faq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FAQ non trouvée",
        )
    updated = await crud_faq.update_faq(db, db_obj=faq, obj_in=payload)
    return updated


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_faq(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin),
):
    """
    Supprime une question de la FAQ (Admin uniquement).
    """
    success = await crud_faq.delete_faq(db, faq_id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FAQ non trouvée",
        )
    return None
