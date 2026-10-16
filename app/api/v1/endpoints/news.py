from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.crud_news import crud_news
from app.schemas.news_article import NewsArticleResponse

router = APIRouter()

@router.get("", response_model=List[NewsArticleResponse])
async def read_news_articles(
    category: Optional[str] = Query(None, description="Filtre par catégorie"),
    search: Optional[str] = Query(None, description="Recherche textuelle"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Récupère les actualités et communiqués officiels de la DGDA avec recherche et filtrage par catégorie.
    """
    articles = await crud_news.get_multi(
        db,
        category=category,
        search=search,
        skip=skip,
        limit=limit,
    )
    return articles

@router.get("/{id}", response_model=NewsArticleResponse)
async def read_news_article(
    id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Récupère le détail d'un article d'actualité DGDA.
    """
    article = await crud_news.get(db, id=id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article d'actualité non trouvé",
        )
    return article
