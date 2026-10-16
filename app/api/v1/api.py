from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    declarations,
    calendar,
    chat,
    documents,
    offices,
    news,
    bookmarks,
)

api_router = APIRouter()

# Authentication & User Management Routes
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Customs Declarations Routes
api_router.include_router(declarations.router, prefix="/declarations", tags=["Declarations"])

# Customs Calendar & Agenda Routes
api_router.include_router(calendar.router, prefix="/calendar", tags=["Calendar Events"])

# Customs AI Chat Assistant Routes
api_router.include_router(chat.router, prefix="/chat", tags=["Agent IA"])

# Official Documents & Regulatory Library Routes
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])

# Customs Offices & Ports Directory Routes
api_router.include_router(offices.router, prefix="/offices", tags=["Offices"])

# Official News & Press Releases Routes
api_router.include_router(news.router, prefix="/news", tags=["News"])

# User Bookmarks & Saved Items Routes
api_router.include_router(bookmarks.router, prefix="/bookmarks", tags=["Bookmarks"])

