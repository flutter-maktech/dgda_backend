from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.crud.crud_declaration import (
    create_declaration,
    delete_declaration,
    get_declaration_by_id,
    get_user_declarations,
    update_declaration,
)
from app.models.user import User
from app.schemas.declaration import (
    DeclarationCreate,
    DeclarationResponse,
    DeclarationUpdate,
)

router = APIRouter()


@router.get(
    "",
    response_model=List[DeclarationResponse],
    summary="List all customs declarations for the current user"
)
async def list_declarations(
    status: Optional[str] = Query(None, description="Filter by status: all, pending, inProgress, validated, rejected"),
    search: Optional[str] = Query(None, description="Search term in reference code, title, or HS code"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve declarations list belonging to the authenticated user.
    """
    declarations = await get_user_declarations(
        db, user_id=current_user.id, status=status, search=search
    )
    return [DeclarationResponse.from_orm_custom(d) for d in declarations]


@router.post(
    "",
    response_model=DeclarationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new customs declaration"
)
async def create_new_declaration(
    declaration_in: DeclarationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new customs declaration submitted by the authenticated user.
    """
    created = await create_declaration(
        db, declaration_in=declaration_in, user_id=current_user.id
    )
    return DeclarationResponse.from_orm_custom(created)


@router.get(
    "/{declaration_id}",
    response_model=DeclarationResponse,
    summary="Get customs declaration details"
)
async def get_declaration(
    declaration_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Fetch full details and fiscal estimates for a single declaration.
    """
    decl = await get_declaration_by_id(db, declaration_id=declaration_id, user_id=current_user.id)
    if not decl:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Déclaration douanière introuvable."
        )
    return DeclarationResponse.from_orm_custom(decl)


@router.patch(
    "/{declaration_id}",
    response_model=DeclarationResponse,
    summary="Update declaration information or status"
)
async def update_existing_declaration(
    declaration_id: int,
    declaration_in: DeclarationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update declaration details or progression status.
    """
    decl = await get_declaration_by_id(db, declaration_id=declaration_id, user_id=current_user.id)
    if not decl:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Déclaration douanière introuvable."
        )
    updated = await update_declaration(db, db_obj=decl, obj_in=declaration_in)
    return DeclarationResponse.from_orm_custom(updated)


@router.delete(
    "/{declaration_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a declaration"
)
async def remove_declaration(
    declaration_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a declaration submitted by the user.
    """
    decl = await get_declaration_by_id(db, declaration_id=declaration_id, user_id=current_user.id)
    if not decl:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Déclaration douanière introuvable."
        )
    await delete_declaration(db, db_obj=decl)
    return {"message": "Déclaration supprimée avec succès."}
