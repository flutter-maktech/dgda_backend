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
    officials,
    uploads,
    partners,
    faqs,
    reports,
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

# Government & DGDA Management Officials Routes
api_router.include_router(officials.router, prefix="/officials", tags=["Leadership & Officials"])

# Official Partners, Sponsors & Recommended Professionals Routes
api_router.include_router(partners.router, prefix="/partners", tags=["Partners & Sponsors"])

# Cloudinary Media Upload Routes (Admin / Media Service)
api_router.include_router(uploads.router, prefix="/uploads", tags=["Media Uploads"])

# Frequently Asked Questions (FAQ) Routes (supports both /faqs and /faq)
api_router.include_router(faqs.router, prefix="/faqs", tags=["FAQ"])
api_router.include_router(faqs.router, prefix="/faq", tags=["FAQ"], include_in_schema=False)

# Discrepancy & Incorrect Data Reports Routes
api_router.include_router(reports.router, prefix="/reports", tags=["Data Reports"])


