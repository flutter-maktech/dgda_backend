from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    get_current_active_admin,
    get_current_user,
    get_current_user_optional,
    get_db,
)
from app.crud.crud_notification import crud_notification
from app.models.user import User
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationUpdate,
)

router = APIRouter()


@router.get("", response_model=List[NotificationResponse])
@router.get("/", response_model=List[NotificationResponse], include_in_schema=False)
async def get_notifications(
    category: Optional[str] = Query(None, description="Category filter (Operational Alert, System Maintenance, etc.)"),
    target_audience: Optional[str] = Query(None, description="Target audience filter"),
    status_filter: Optional[str] = Query(None, alias="status", description="Status filter (delivered, broadcasting, scheduled)"),
    search: Optional[str] = Query(None, description="Search term in title, subtitle, body"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Récupère la liste des notifications et alertes officielles de la DGDA.
    Si l'utilisateur est authentifié, retourne l'état de lecture personnalisé (is_read / is_unread).
    """
    notifications = await crud_notification.get_all_notifications(
        db=db,
        category=category,
        target_audience=target_audience,
        status=status_filter,
        search=search,
    )

    read_ids = set()
    if current_user:
        read_ids = await crud_notification.get_user_read_notification_ids(
            db=db, user_id=current_user.id
        )

    res = []
    for notif in notifications:
        is_read = notif.id in read_ids
        data = NotificationResponse.model_validate(notif)
        data.is_read = is_read
        data.is_unread = not is_read
        res.append(data)
    return res


@router.post("/read-all")
async def mark_all_notifications_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Marque toutes les notifications comme lues pour l'utilisateur connecté.
    """
    count = await crud_notification.mark_all_as_read(db, user_id=current_user.id)
    return {
        "success": True,
        "marked_count": count,
        "message": f"{count} notifications ont été marquées comme lues",
    }


@router.post("/{id}/read")
async def mark_notification_read(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Marque une notification spécifique comme lue pour l'utilisateur connecté.
    """
    notif = await crud_notification.get_notification_by_id(db, notif_id=id)
    if not notif:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification introuvable",
        )
    await crud_notification.mark_as_read(
        db=db, user_id=current_user.id, notification_id=id
    )
    return {
        "success": True,
        "notification_id": id,
        "is_read": True,
        "message": "Notification marquée comme lue avec succès",
    }


@router.get("/{id}", response_model=NotificationResponse)
async def get_notification(
    id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Récupère le détail d'une notification par son identifiant.
    """
    notif = await crud_notification.get_notification_by_id(db, notif_id=id)
    if not notif:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification introuvable",
        )
    return notif


@router.post(
    "",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_notification(
    payload: NotificationCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin),
):
    """
    Crée et diffuse une nouvelle notification (Admin uniquement).
    """
    new_notif = await crud_notification.create_notification(db, obj_in=payload)
    return new_notif


@router.put("/{id}", response_model=NotificationResponse)
async def update_notification(
    id: str,
    payload: NotificationUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin),
):
    """
    Met à jour une notification existante (Admin uniquement).
    """
    notif = await crud_notification.get_notification_by_id(db, notif_id=id)
    if not notif:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification introuvable",
        )
    updated = await crud_notification.update_notification(db, db_obj=notif, obj_in=payload)
    return updated


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin),
):
    """
    Supprime une notification (Admin uniquement).
    """
    success = await crud_notification.delete_notification(db, notif_id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification introuvable",
        )
    return None
