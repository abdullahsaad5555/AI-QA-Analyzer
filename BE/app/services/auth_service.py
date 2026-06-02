# app/services/auth_service.py

from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    generate_otp,
    hash_otp,
    verify_otp,
)
from app.models.otp import EmailOTP
from app.models.users import User


class AuthService:
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user(db: AsyncSession, email: str) -> User:
        user = User(email=email)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def get_or_create_user(db: AsyncSession, email: str) -> User:
        user = await AuthService.get_user_by_email(db, email)
        if user:
            return user
        return await AuthService.create_user(db, email)

    @staticmethod
    async def invalidate_existing_otps(db: AsyncSession, email: str) -> None:
        """
        Mark all active OTPs for this email as consumed before creating a new one.
        """
        result = await db.execute(
            select(EmailOTP).where(
                EmailOTP.email == email,
                EmailOTP.consumed.is_(False),
            )
        )
        existing_otps = result.scalars().all()

        for otp_record in existing_otps:
            otp_record.consumed = True

        if existing_otps:
            await db.commit()

    @staticmethod
    async def create_otp(db: AsyncSession, email: str) -> str:
        """
        Creates a fresh OTP, stores only the hash, and returns the plain OTP
        so the caller can deliver it via email.
        
        IMPORTANT:
        Do not return this plain OTP to the frontend in production.
        It should only be sent through your email provider.
        """
        await AuthService.invalidate_existing_otps(db, email)

        plain_otp = generate_otp()
        otp_record = EmailOTP(
            email=email,
            code_hash=hash_otp(plain_otp),
            expires_at=EmailOTP.build_expiry(),
            attempts=0,
            consumed=False,
        )

        db.add(otp_record)
        await db.commit()
        await db.refresh(otp_record)

        return plain_otp

    @staticmethod
    async def get_latest_active_otp(db: AsyncSession, email: str) -> EmailOTP | None:
        result = await db.execute(
            select(EmailOTP)
            .where(
                EmailOTP.email == email,
                EmailOTP.consumed.is_(False),
            )
            .order_by(desc(EmailOTP.created_at))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def verify_email_otp(
        db: AsyncSession,
        email: str,
        plain_otp: str,
    ) -> dict:
        otp_record = await AuthService.get_latest_active_otp(db, email)

        if not otp_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active OTP found for this email",
            )

        if otp_record.expires_at < datetime.utcnow():
            otp_record.consumed = True
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP has expired",
            )

        if otp_record.attempts >= settings.OTP_MAX_ATTEMPTS:
            otp_record.consumed = True
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum OTP attempts exceeded",
            )

        if not verify_otp(plain_otp, otp_record.code_hash):
            otp_record.attempts += 1
            if otp_record.attempts >= settings.OTP_MAX_ATTEMPTS:
                otp_record.consumed = True
            await db.commit()

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP",
            )

        otp_record.consumed = True
        await db.commit()

        user = await AuthService.get_or_create_user(db, email)

        access_token = create_access_token(subject=str(user.id))
        refresh_token = create_refresh_token(subject=str(user.id))

        return {
            "message": "Login successful",
            "user": user,
            "tokens": {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            },
        }
