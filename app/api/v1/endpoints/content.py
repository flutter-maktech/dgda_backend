from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_admin, get_db
from app.crud.crud_content import crud_content
from app.models.user import User
from app.schemas.content_document import (
    ContentDocumentResponse,
    ContentDocumentUpdate,
    ContentDocumentWrappedResponse,
)

router = APIRouter()


def _wrap_response(doc) -> Dict[str, Any]:
    """Format document according to Flutter and Admin Dashboard standard responses."""
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document introuvable",
        )
    return {
        "statusCode": 200,
        "success": True,
        "message": "Document récupéré avec succès",
        "data": {
            "id": doc.id,
            "type": doc.type,
            "title": doc.title,
            "cardTitle": doc.card_title,
            "heroTitle": doc.hero_title,
            "subtitle": doc.subtitle,
            "content": doc.content,
            "paragraphs": doc.paragraphs or [],
            "lastUpdated": doc.last_updated,
            "is_published": doc.is_published,
            "created_at": doc.created_at.isoformat() if doc.created_at else None,
            "updated_at": doc.updated_at.isoformat() if doc.updated_at else None,
        },
    }


# =========================================================================
# Public Endpoints for Mobile App & Web (supporting multiple URL patterns)
# =========================================================================

@router.get("/privacy-policy")
@router.get("/rule/privacy-policy", include_in_schema=False)
async def get_privacy_policy(db: AsyncSession = Depends(get_db)):
    """Récupère la Politique de Confidentialité officielle de la DGDA."""
    doc = await crud_content.get_by_type(db, "privacy-policy")
    return _wrap_response(doc)


@router.get("/about-us")
@router.get("/rule/about", include_in_schema=False)
async def get_about_us(db: AsyncSession = Depends(get_db)):
    """Récupère la présentation officielle de la DGDA (À propos)."""
    doc = await crud_content.get_by_type(db, "about-us")
    return _wrap_response(doc)


@router.get("/terms-and-conditions")
@router.get("/rule/terms-and-conditions", include_in_schema=False)
async def get_terms_and_conditions(db: AsyncSession = Depends(get_db)):
    """Récupère les Conditions Générales d'Utilisation (CGU)."""
    doc = await crud_content.get_by_type(db, "terms-and-condition")
    return _wrap_response(doc)


@router.get("/documents/{doc_type}")
async def get_document_by_type(doc_type: str, db: AsyncSession = Depends(get_db)):
    """Récupère un document légal par son identifiant de type."""
    doc = await crud_content.get_by_type(db, doc_type)
    return _wrap_response(doc)


# =========================================================================
# Admin Dashboard Compatible Endpoints (/admin/side-content/{type}/{id})
# =========================================================================

@router.get("/admin/side-content/{doc_type}/{doc_id}")
async def get_admin_side_content(
    doc_type: str,
    doc_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Récupère le document pour l'éditeur du tableau de bord administrateur."""
    doc = await crud_content.get_by_type(db, doc_type)
    if not doc:
        doc = await crud_content.get_by_id(db, doc_id)
    return _wrap_response(doc)


@router.patch("/admin/side-content/{doc_type}/{doc_id}")
@router.post("/admin/side-content/{doc_type}/{doc_id}", include_in_schema=False)
async def update_admin_side_content(
    doc_type: str,
    doc_id: str,
    payload: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin),
):
    """Met à jour un document légal depuis l'éditeur d'administration."""
    title = payload.get("title")
    content = payload.get("content")

    doc = await crud_content.create_or_update_by_type(
        db=db,
        doc_type=doc_type,
        title=title,
        content=content,
    )
    return _wrap_response(doc)


@router.put("/documents/{doc_type}", response_model=ContentDocumentResponse)
async def update_document(
    doc_type: str,
    payload: ContentDocumentUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin),
):
    """Mise à jour complète d'un document légal (Admin uniquement)."""
    doc = await crud_content.get_by_type(db, doc_type)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document introuvable",
        )
    updated = await crud_content.update(db, db_obj=doc, obj_in=payload)
    return updated
