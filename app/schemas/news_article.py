from pydantic import BaseModel, ConfigDict
from typing import Optional

class NewsArticleBase(BaseModel):
    title: str
    subtitle: str
    content: Optional[str] = None
    date: str
    category: str
    image_url: Optional[str] = None
    pdf_url: Optional[str] = None
    is_featured: Optional[bool] = False

class NewsArticleCreate(NewsArticleBase):
    pass

class NewsArticleResponse(NewsArticleBase):
    id: str
    is_favorite: Optional[bool] = False
    is_bookmarked: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)
