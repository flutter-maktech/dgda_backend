from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_active_staff
from app.schemas.customs_document import (
    CustomsDocumentResponse,
    CustomsDocumentCreate,
    CustomsDocumentUpdate,
)
from app.crud import crud_document

router = APIRouter()


@router.get(
    "",
    response_model=List[CustomsDocumentResponse],
    summary="List all official DGDA customs documents and regulatory guides",
)
async def list_documents(
    category: Optional[str] = Query(None, description="Filter by category (e.g. Tariffs & Codes, Procedures & Forms)"),
    search: Optional[str] = Query(None, description="Search term for title or description"),
    db: AsyncSession = Depends(get_db),
):
    docs = await crud_document.get_documents(db=db, category=category, search=search)
    return docs


@router.get(
    "/{document_id}",
    response_model=CustomsDocumentResponse,
    summary="Get single customs document details",
)
async def get_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
):
    doc = await crud_document.get_document_by_id(db=db, document_id=document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    return doc


@router.post(
    "",
    response_model=CustomsDocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create official customs document (Admin / Staff)",
)
async def create_document(
    doc_in: CustomsDocumentCreate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_active_staff),
):
    return await crud_document.create_document(db, doc_in=doc_in)


@router.put(
    "/{document_id}",
    response_model=CustomsDocumentResponse,
    summary="Update official customs document (Admin / Staff)",
)
@router.patch(
    "/{document_id}",
    response_model=CustomsDocumentResponse,
    summary="Patch official customs document (Admin / Staff)",
)
async def update_document(
    document_id: int,
    doc_in: CustomsDocumentUpdate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_active_staff),
):
    doc = await crud_document.update_document(db, document_id=document_id, doc_in=doc_in)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    return doc


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete customs document (Admin / Staff)",
)
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_active_staff),
):
    success = await crud_document.delete_document(db, document_id=document_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    return {"success": True, "message": "Document deleted successfully", "id": document_id}
