from fastapi import APIRouter
from app.api.v1.endpoints import auth, declarations, calendar, chat

api_router = APIRouter()

# Authentication & User Management Routes
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Customs Declarations Routes
api_router.include_router(declarations.router, prefix="/declarations", tags=["Declarations"])

# Customs Calendar & Agenda Routes
api_router.include_router(calendar.router, prefix="/calendar", tags=["Calendar Events"])

# Customs AI Chat Assistant Routes
api_router.include_router(chat.router, prefix="/chat", tags=["Agent IA"])

