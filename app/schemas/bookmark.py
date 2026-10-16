from pydantic import BaseModel
from typing import List, Optional


class BookmarkToggleRequest(BaseModel):
    item_type: str  # "news", "document", "office"
    item_id: str


class BookmarkToggleResponse(BaseModel):
    item_type: str
    item_id: str
    is_bookmarked: bool
    message: str


class UserBookmarksIdsResponse(BaseModel):
    news: List[str]
    documents: List[str]
    offices: List[str]
