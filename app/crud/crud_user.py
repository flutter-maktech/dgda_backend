from typing import Any, Dict, List, Optional, Union
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """Retrieve a user by their primary key ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Retrieve a user by their email address."""
    result = await db.execute(select(User).where(User.email == email.lower()))
    return result.scalars().first()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """Retrieve a user by their username."""
    if not username:
        return None
    result = await db.execute(select(User).where(User.username == username.lower()))
    return result.scalars().first()


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    """Create a new user with hashed password."""
    db_user = User(
        email=user_in.email.lower(),
        username=user_in.username.lower() if user_in.username else None,
        full_name=user_in.full_name,
        phone_number=user_in.phone_number,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role or "USER",
        is_active=True,
        is_verified=False,
    )
    db.add(db_user)
    await db.flush()
    await db.refresh(db_user)
    return db_user


async def authenticate(
    db: AsyncSession, email: str, password: str
) -> Optional[User]:
    """Authenticate user with email and plain password."""
    user = await get_user_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def update_user(
    db: AsyncSession,
    db_user: User,
    user_in: Union[UserUpdate, Dict[str, Any]]
) -> User:
    """Update existing user record."""
    if isinstance(user_in, dict):
        update_data = user_in
    else:
        update_data = user_in.model_dump(exclude_unset=True)

    if "password" in update_data and update_data["password"]:
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password

    if "email" in update_data and update_data["email"]:
        update_data["email"] = update_data["email"].lower()

    if "username" in update_data and update_data["username"]:
        update_data["username"] = update_data["username"].lower()

    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.add(db_user)
    await db.flush()
    await db.refresh(db_user)
    return db_user


async def get_users_list(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> List[User]:
    """Paginated list of users for administration."""
    result = await db.execute(select(User).offset(skip).limit(limit))
    return list(result.scalars().all())
