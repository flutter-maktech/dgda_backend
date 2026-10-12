import random
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
from app.crud.crud_otp import create_otp, verify_otp
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
    ForgotPasswordRequest,
    PasswordChangeRequest,
    RefreshTokenRequest,
    ResetPasswordWithOtpRequest,
    SendOtpRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
    VerifyOtpRequest,
)
from app.services.email_service import send_otp_email

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
    # Ensure username uniqueness automatically without blocking registration
    clean_username = user_in.username.lower().strip() if user_in.username else None
    if clean_username:
        base_name = clean_username
        while True:
            existing_username = await get_user_by_username(db, username=clean_username)
            if existing_username and existing_username.email != user_in.email.lower():
                clean_username = f"{base_name}_{random.randint(100, 9999)}"
            else:
                break

    # Check if email is already registered
    existing_user = await get_user_by_email(db, email=user_in.email)
    if existing_user:
        if not existing_user.is_verified:
            # User previously registered but never finished OTP verification.
            # Allow them to refresh their credentials and proceed with verification.
            existing_user.full_name = user_in.full_name
            if user_in.phone_number:
                existing_user.phone_number = user_in.phone_number
            existing_user.hashed_password = get_password_hash(user_in.password)
            if clean_username:
                existing_user.username = clean_username
            db.add(existing_user)
            await db.commit()
            await db.refresh(existing_user)
            user = existing_user
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un compte avec cette adresse e-mail existe déjà. Veuillez vous connecter."
            )
    else:
        # By default, public registration creates regular USER role
        user_data = user_in.model_copy()
        user_data.role = UserRole.USER
        if clean_username:
            user_data.username = clean_username
        user = await create_user(db, user_in=user_data)


    # Automatically generate and dispatch verification OTP email via Resend
    try:
        otp_code = await create_otp(db, email=user.email, purpose="VERIFICATION")
        print(f"Generated OTP for {user.email}: {otp_code}")
        send_otp_email(to_email=user.email, otp_code=otp_code, purpose="VERIFICATION")
    except Exception as e:
        print(f"Notice: Failed to dispatch initial OTP via Resend: {e}")

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


@router.post(
    "/send-otp",
    status_code=status.HTTP_200_OK,
    summary="Generate and send OTP code to email via Resend"
)
@router.post(
    "/resend-otp",
    status_code=status.HTTP_200_OK,
    summary="Resend OTP code to email via Resend"
)
@limiter.limit("5/minute")
async def send_otp(
    request: Request,
    otp_req: SendOtpRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a 6-digit OTP code, save in database, and dispatch an email via Resend.
    """
    otp_code = await create_otp(db, email=otp_req.email, purpose=otp_req.purpose or "VERIFICATION")
    
    # Send email through Resend API
    email_sent = send_otp_email(
        to_email=otp_req.email,
        otp_code=otp_code,
        purpose=otp_req.purpose or "VERIFICATION"
    )

    if not email_sent:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Échec de l'envoi de l'e-mail via Resend. Veuillez vérifier votre adresse e-mail."
        )

    return {
        "message": "Code de vérification envoyé avec succès.",
        "email": otp_req.email,
        "expires_in_minutes": settings.OTP_EXPIRE_MINUTES
    }


@router.post(
    "/verify-otp",
    status_code=status.HTTP_200_OK,
    summary="Verify submitted OTP code"
)
async def verify_user_otp(
    verify_req: VerifyOtpRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Validate user OTP. If purpose is VERIFICATION, mark the user account as verified.
    """
    code = verify_req.get_code()
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le code de vérification est requis."
        )

    clean_email = str(verify_req.email).lower().strip()
    purpose = (verify_req.purpose or "VERIFICATION").strip().upper()

    is_valid = await verify_otp(
        db,
        email=clean_email,
        code=code,
        purpose=purpose
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code de vérification incorrect ou expiré."
        )

    # If verification is for account activation, update user is_verified status
    user = await get_user_by_email(db, email=clean_email)
    if user and purpose == "VERIFICATION":
        user.is_verified = True
        db.add(user)
        await db.commit()

    return {
        "message": "Vérification réussie avec succès.",
        "verified": True,
        "email": clean_email
    }


@router.post(
    "/forgot-password",
    status_code=status.HTTP_200_OK,
    summary="Send password reset OTP via Resend"
)
@limiter.limit("5/minute")
async def forgot_password(
    request: Request,
    forgot_req: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate password reset OTP and dispatch via Resend.
    """
    clean_email = str(forgot_req.email).lower().strip()
    user = await get_user_by_email(db, email=clean_email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucun compte associé à cette adresse e-mail n'a été trouvé."
        )

    otp_code = await create_otp(db, email=clean_email, purpose="PASSWORD_RESET")
    print(f"Generated password reset OTP for {clean_email}: {otp_code}")
    email_sent = send_otp_email(
        to_email=clean_email,
        otp_code=otp_code,
        purpose="PASSWORD_RESET"
    )

    if not email_sent:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Échec de l'envoi de l'e-mail de réinitialisation."
        )

    return {
        "message": "Un code de réinitialisation a été envoyé à votre adresse e-mail.",
        "email": clean_email
    }


@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
    summary="Reset password using verified OTP"
)
async def reset_password(
    reset_req: ResetPasswordWithOtpRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify OTP for PASSWORD_RESET purpose and update to new password.
    """
    code = reset_req.get_code()
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le code de réinitialisation est requis."
        )

    clean_email = str(reset_req.email).lower().strip()
    is_valid = await verify_otp(
        db,
        email=clean_email,
        code=code,
        purpose="PASSWORD_RESET"
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code de réinitialisation incorrect ou expiré."
        )


    user = await get_user_by_email(db, email=reset_req.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé."
        )

    await update_user(db, db_user=user, user_in={"password": reset_req.new_password})
    return {"message": "Votre mot de passe a été réinitialisé avec succès."}

