from datetime import datetime
from typing import Optional, Union
from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


# Shared Properties
class UserBase(BaseModel):
    email: EmailStr
    username: Optional[str] = None
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    company_name: Optional[str] = None
    company_nif: Optional[str] = None
    profile_image: Optional[str] = None


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
    fullName: Optional[str] = None
    phone_number: Optional[str] = None
    phoneNumber: Optional[str] = None
    mobileNumber: Optional[str] = None
    company_name: Optional[str] = None
    companyName: Optional[str] = None
    company_nif: Optional[str] = None
    companyNif: Optional[str] = None
    profile_image: Optional[str] = None
    profileImage: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6, max_length=128)
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None


# Schema for Changing Password
class PasswordChangeRequest(BaseModel):
    current_password: Optional[str] = None
    currentPassword: Optional[str] = None
    new_password: Optional[str] = None
    newPassword: Optional[str] = None
    confirm_password: Optional[str] = None
    confirmPassword: Optional[str] = None

    def get_current_password(self) -> str:
        return (self.current_password or self.currentPassword or "").strip()

    def get_new_password(self) -> str:
        return (self.new_password or self.newPassword or "").strip()



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
    otp: Optional[Union[str, int]] = None
    oneTimeCode: Optional[Union[str, int]] = None
    purpose: Optional[str] = "VERIFICATION"

    def get_code(self) -> str:
        if self.otp is not None and str(self.otp).strip():
            return str(self.otp).strip()
        if self.oneTimeCode is not None and str(self.oneTimeCode).strip():
            return str(self.oneTimeCode).strip()
        return ""


# Schema for Forgot Password
class ForgotPasswordRequest(BaseModel):
    email: EmailStr


# Schema for Resetting Password with OTP
class ResetPasswordWithOtpRequest(BaseModel):
    email: Optional[EmailStr] = None
    otp: Optional[Union[str, int]] = None
    oneTimeCode: Optional[Union[str, int]] = None
    new_password: Optional[str] = None
    newPassword: Optional[str] = None
    confirm_password: Optional[str] = None
    confirmPassword: Optional[str] = None
    token: Optional[str] = None

    def get_code(self) -> str:
        if self.otp is not None and str(self.otp).strip():
            return str(self.otp).strip()
        if self.oneTimeCode is not None and str(self.oneTimeCode).strip():
            return str(self.oneTimeCode).strip()
        return ""

    def get_password(self) -> str:
        return (self.new_password or self.newPassword or "").strip()

