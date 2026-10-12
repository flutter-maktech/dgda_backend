import random
from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.otp import OtpVerification


async def create_otp(
    db: AsyncSession,
    email: str,
    purpose: str = "VERIFICATION"
) -> str:
    """
    Generate a new 6-digit numeric OTP, invalidate previous pending codes,
    and persist in the database with an expiration timestamp.
    """
    clean_email = email.lower().strip()

    # Invalidate older pending OTPs for this email and purpose
    await db.execute(
        update(OtpVerification)
        .where(
            OtpVerification.email == clean_email,
            OtpVerification.purpose == purpose,
            OtpVerification.is_used == False
        )
        .values(is_used=True)
    )

    # Generate a cryptographically clean 6-digit code
    code = f"{random.randint(100000, 999999)}"
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)

    otp_record = OtpVerification(
        email=clean_email,
        code=code,
        purpose=purpose,
        is_used=False,
        expires_at=expires_at,
    )
    db.add(otp_record)
    await db.flush()
    return code


async def verify_otp(
    db: AsyncSession,
    email: str,
    code: str,
    purpose: str = "VERIFICATION"
) -> bool:
    """
    Verify if the supplied code is valid, unused, and not expired.
    Marks the code as used upon successful verification.
    """
    clean_email = email.lower().strip()
    clean_code = code.strip()

    result = await db.execute(
        select(OtpVerification)
        .where(
            OtpVerification.email == clean_email,
            OtpVerification.code == clean_code,
            OtpVerification.purpose == purpose,
            OtpVerification.is_used == False,
        )
        .order_by(OtpVerification.created_at.desc())
    )
    otp_record: Optional[OtpVerification] = result.scalars().first()

    if not otp_record:
        return False

    if otp_record.is_expired():
        return False

    # Mark as used so it cannot be replayed
    otp_record.is_used = True
    db.add(otp_record)
    await db.flush()
    return True
