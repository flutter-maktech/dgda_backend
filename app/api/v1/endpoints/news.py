from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_active_staff
from app.crud.crud_news import crud_news
from app.schemas.news_article import NewsArticleResponse, NewsArticleCreate, NewsArticleUpdate

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

@router.post("", response_model=NewsArticleResponse, status_code=status.HTTP_201_CREATED)
async def create_news_article(
    article_in: NewsArticleCreate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_active_staff),
):
    """
    Create a new official news article or press bulletin (Admin / Staff).
    """
    return await crud_news.create(db, obj_in=article_in)

@router.put("/{id}", response_model=NewsArticleResponse)
@router.patch("/{id}", response_model=NewsArticleResponse)
async def update_news_article(
    id: str,
    article_in: NewsArticleUpdate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_active_staff),
):
    """
    Update an existing news article (Admin / Staff).
    """
    article = await crud_news.get(db, id=id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article d'actualité non trouvé",
        )
    return await crud_news.update(db, db_obj=article, obj_in=article_in)

@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_news_article(
    id: str,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_active_staff),
):
    """
    Delete a news article (Admin / Staff).
    """
    success = await crud_news.delete(db, id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article d'actualité non trouvé",
        )
    return {"success": True, "message": "Article deleted successfully", "id": id}
