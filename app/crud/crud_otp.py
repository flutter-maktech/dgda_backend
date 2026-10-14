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
    Generate a new 6-digit numeric OTP and persist immediately in the database
    with an expiration timestamp.
    """
    clean_email = email.lower().strip()
    clean_purpose = purpose.strip().upper()

    # Generate a cryptographically clean 6-digit code
    code = f"{random.randint(100000, 999999)}"
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)

    otp_record = OtpVerification(
        email=clean_email,
        code=code,
        purpose=clean_purpose,
        is_used=False,
        expires_at=expires_at,
    )
    db.add(otp_record)
    await db.commit()
    await db.refresh(otp_record)
    return code


async def verify_otp(
    db: AsyncSession,
    email: str,
    code: str,
    purpose: str = "VERIFICATION",
    mark_used: bool = True,
) -> bool:
    """
    Verify if the supplied code is valid, unused, and not expired.
    If mark_used is True, marks all pending codes for this email and purpose as used.
    """
    clean_email = email.lower().strip()
    clean_code = code.strip()
    clean_purpose = purpose.strip().upper()

    result = await db.execute(
        select(OtpVerification)
        .where(
            OtpVerification.email == clean_email,
            OtpVerification.code == clean_code,
            OtpVerification.purpose == clean_purpose,
            OtpVerification.is_used == False,
        )
        .order_by(OtpVerification.created_at.desc())
    )
    otp_record: Optional[OtpVerification] = result.scalars().first()

    if not otp_record:
        return False

    if otp_record.is_expired():
        return False

    if mark_used:
        # Mark all pending codes for this email and purpose as used so none can be replayed
        await db.execute(
            update(OtpVerification)
            .where(
                OtpVerification.email == clean_email,
                OtpVerification.purpose == clean_purpose,
            )
            .values(is_used=True)
        )
        await db.commit()
    return True

