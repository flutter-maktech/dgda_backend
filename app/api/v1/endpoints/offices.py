from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.schemas.customs_office import CustomsOfficeResponse
from app.crud import crud_office

router = APIRouter()


@router.get(
    "",
    response_model=List[CustomsOfficeResponse],
    summary="List all DGDA customs bureaus, ports and border posts",
)
async def list_offices(
    region: Optional[str] = Query(None, description="Filter by region (e.g. Kongo Central, Haut-Katanga, Kinshasa)"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (open, closed, all)"),
    search: Optional[str] = Query(None, description="Search term for name, code, or location"),
    db: AsyncSession = Depends(get_db),
):
    offices = await crud_office.get_offices(
        db=db,
        region=region,
        status=status_filter,
        search=search,
    )
    return offices


@router.get(
    "/{office_id}",
    response_model=CustomsOfficeResponse,
    summary="Get single customs office details",
)
async def get_office(
    office_id: int,
    db: AsyncSession = Depends(get_db),
):
    office = await crud_office.get_office_by_id(db=db, office_id=office_id)
    if not office:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customs office not found",
        )
    return office
