from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.schemas.customs_document import CustomsDocumentResponse
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
