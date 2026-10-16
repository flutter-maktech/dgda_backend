from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.crud.crud_bookmark import crud_bookmark
from app.models.user import User
from app.schemas.bookmark import (
    BookmarkToggleRequest,
    BookmarkToggleResponse,
    UserBookmarksIdsResponse,
)

router = APIRouter()


@router.get("/ids", response_model=UserBookmarksIdsResponse)
async def get_my_bookmarks_ids(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Récupère la liste de tous les IDs d'éléments enregistrés par l'utilisateur connecté (News, Documents, Bureaux).
    """
    bookmarks = await crud_bookmark.get_user_bookmark_ids(db, user_id=current_user.id)
    return bookmarks


@router.post("/toggle", response_model=BookmarkToggleResponse)
async def toggle_bookmark(
    payload: BookmarkToggleRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Ajoute ou supprime un signet (News, Document, Bureau) pour l'utilisateur connecté.
    """
    is_bookmarked = await crud_bookmark.toggle(
        db,
        user_id=current_user.id,
        item_type=payload.item_type,
        item_id=payload.item_id,
    )
    message = (
        "Élément ajouté aux favoris avec succès"
        if is_bookmarked
        else "Élément retiré des favoris avec succès"
    )
    return BookmarkToggleResponse(
        item_type=payload.item_type,
        item_id=payload.item_id,
        is_bookmarked=is_bookmarked,
        message=message,
    )


@router.post("/{item_type}/{item_id}/toggle", response_model=BookmarkToggleResponse)
async def toggle_specific_bookmark(
    item_type: str,
    item_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Endpoint direct pour basculer l'état de favori d'un élément spécifique.
    item_type: 'news' | 'document' | 'office'
    """
    is_bookmarked = await crud_bookmark.toggle(
        db,
        user_id=current_user.id,
        item_type=item_type,
        item_id=item_id,
    )
    message = (
        "Élément ajouté aux favoris avec succès"
        if is_bookmarked
        else "Élément retiré des favoris avec succès"
    )
    return BookmarkToggleResponse(
        item_type=item_type,
        item_id=item_id,
        is_bookmarked=is_bookmarked,
        message=message,
    )


@router.get("/{item_type}", response_model=List[str])
async def get_bookmarked_ids_by_type(
    item_type: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Récupère la liste des IDs enregistrés pour une catégorie donnée ('news', 'document', 'office').
    """
    ids = await crud_bookmark.get_ids_by_type(
        db,
        user_id=current_user.id,
        item_type=item_type,
    )
    return ids
