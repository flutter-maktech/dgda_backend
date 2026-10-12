from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


# Shared Properties
class UserBase(BaseModel):
    email: EmailStr
    username: Optional[str] = None
    full_name: Optional[str] = None
    phone_number: Optional[str] = None


# Schema for User Registration
class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128, description="User password (min 6 chars)")
    role: Optional[UserRole] = UserRole.USER


# Schema for User Login
class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


# Schema for Updating User
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6, max_length=128)
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None


# Schema for Changing Password
class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6, max_length=128)


# Schema for User Out / Response
class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Schema for JWT Authentication Response
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


# Schema for Refreshing Access Token
class RefreshTokenRequest(BaseModel):
    refresh_token: str


# Schema for Decoded Token Payload
class TokenPayload(BaseModel):
    sub: str
    role: Optional[str] = "user"
    type: Optional[str] = "access"
    exp: Optional[int] = None


# Schema for Sending / Resending OTP
class SendOtpRequest(BaseModel):
    email: EmailStr
    purpose: Optional[str] = "VERIFICATION"


# Schema for Verifying OTP
class VerifyOtpRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=4, max_length=10)
    purpose: Optional[str] = "VERIFICATION"


# Schema for Forgot Password
class ForgotPasswordRequest(BaseModel):
    email: EmailStr


# Schema for Resetting Password with OTP
class ResetPasswordWithOtpRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=4, max_length=10)
    new_password: str = Field(..., min_length=6, max_length=128)

