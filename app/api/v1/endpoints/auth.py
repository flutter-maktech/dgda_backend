from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.config import settings
from app.core.limiter import limiter
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.crud.crud_user import (
    authenticate,
    create_user,
    get_user_by_email,
    get_user_by_id,
    get_user_by_username,
    update_user,
)
from app.models.user import User, UserRole
from app.schemas.user import (
    PasswordChangeRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
)

router = APIRouter()


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account"
)
@limiter.limit(settings.RATE_LIMIT_REGISTER)
async def register(
    request: Request,
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user, automatically hash the password,
    and return an access + refresh token.
    """
    # Check if email is already registered
    existing_user = await get_user_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists."
        )

    # Check if username is already taken
    if user_in.username:
        existing_username = await get_user_by_username(db, username=user_in.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this username already exists."
            )

    # By default, public registration creates regular USER role
    user_data = user_in.model_copy()
    user_data.role = UserRole.USER

    user = await create_user(db, user_in=user_data)

    # Generate JWT tokens
    access_token = create_access_token(subject=user.id, role=user.role.value)
    refresh_token = create_refresh_token(subject=user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login with email and password"
)
@limiter.limit(settings.RATE_LIMIT_LOGIN)
async def login(
    request: Request,
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user credentials, check account status,
    and return fresh access + refresh tokens.
    """
    user = await authenticate(db, email=credentials.email, password=credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This account has been deactivated. Please contact support.",
        )

    access_token = create_access_token(subject=user.id, role=user.role.value)
    refresh_token = create_refresh_token(subject=user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Obtain a new access token using a refresh token"
)
async def refresh_token(
    refresh_req: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify the validity of a refresh token and issue a fresh token pair.
    """
    payload = decode_token(refresh_req.refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token."
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type provided."
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing user identity."
        )

    user = await get_user_by_id(db, user_id=int(user_id))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or account is deactivated."
        )

    # Create new pair
    access_token = create_access_token(subject=user.id, role=user.role.value)
    new_refresh_token = create_refresh_token(subject=user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user profile"
)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """
    Return the profile details of the currently authenticated user.
    """
    return UserResponse.model_validate(current_user)


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update current user profile information"
)
async def update_me(
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update profile details for the logged-in user.
    """
    # Prevent regular users from self-promoting to admin
    update_data = user_update.model_dump(exclude_unset=True)
    if "role" in update_data and current_user.role != UserRole.ADMIN:
        del update_data["role"]

    updated = await update_user(db, db_user=current_user, user_in=update_data)
    return UserResponse.model_validate(updated)


@router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
    summary="Change user password"
)
async def change_password(
    pwd_in: PasswordChangeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Validate the existing password and update with a new hashed password.
    """
    if not verify_password(pwd_in.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password entered is incorrect."
        )

    await update_user(db, db_user=current_user, user_in={"password": pwd_in.new_password})
    return {"message": "Password changed successfully."}
