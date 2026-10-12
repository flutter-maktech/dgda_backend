from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import select

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import AsyncSessionLocal, init_db
from app.core.limiter import limiter
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.otp import OtpVerification


async def seed_initial_admin() -> None:
    """Seed default administrator account if the database has no admin."""
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(
                select(User).where(User.role == UserRole.ADMIN)
            )
            existing_admin = result.scalars().first()
            if not existing_admin:
                default_admin = User(
                    email="admin@dgda.gouv.cd",
                    username="admin_dgda",
                    full_name="Administrateur DGDA",
                    phone_number="+243821920215",
                    hashed_password=get_password_hash("Admin@DGDA2026!"),
                    role=UserRole.ADMIN,
                    is_active=True,
                    is_verified=True,
                )
                session.add(default_admin)
                await session.commit()
                print("Default administrator seeded: admin@dgda.gouv.cd / Admin@DGDA2026!")
        except Exception as e:
            await session.rollback()
            print(f"Error seeding initial admin: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown routines."""
    # Startup: Initialize Database Tables and default Admin
    await init_db()
    await seed_initial_admin()
    yield
    # Shutdown routine (if needed)


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Official API for DGDA Mobile App & Admin Portal",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Attach Rate Limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Middleware for Cross-Platform App & Web Admin
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS if isinstance(settings.BACKEND_CORS_ORIGINS, list) else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 Endpoints
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint verifying API status."""
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "documentation": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
    }
