# app/api/v1/auth.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.schemas.auth import (
    SendOTPRequest,
    SendOTPResponse,
    VerifyOTPRequest,
    VerifyOTPResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/send-otp",
    response_model=SendOTPResponse,
    status_code=status.HTTP_200_OK,
)
async def send_otp(
    payload: SendOTPRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Generate an OTP for the provided email and store its hash in the database.

    NOTE:
    Replace the temporary print() statement with a real email provider
    (SMTP, Resend, SendGrid, SES, etc.) before production use.
    """
    otp = await AuthService.create_otp(db, payload.email)

    # TEMPORARY for local development/testing only
    print(f"[DEV OTP] Email: {payload.email} | OTP: {otp}")

    return SendOTPResponse(message="OTP sent successfully")


@router.post(
    "/verify-otp",
    response_model=VerifyOTPResponse,
    status_code=status.HTTP_200_OK,
)
async def verify_otp(
    payload: VerifyOTPRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Verify the submitted OTP, create the user if needed,
    and return access + refresh tokens.
    """
    result = await AuthService.verify_email_otp(
        db=db,
        email=payload.email,
        plain_otp=payload.otp,
    )

    return VerifyOTPResponse(
        message=result["message"],
        user=result["user"],
        tokens=result["tokens"],
    )