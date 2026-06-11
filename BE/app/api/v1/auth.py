from fastapi import APIRouter, BackgroundTasks, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.schemas.auth import (
    SendOTPRequest,
    SendOTPResponse,
    VerifyOTPRequest,
    VerifyOTPResponse,
)
from app.services.auth_service import AuthService
from app.services.mail_service import send_otp_email

# Shared limiter instance (see small companion file below)
from app.core.rate_limit import limiter

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/send-otp",
    response_model=SendOTPResponse,
    status_code=status.HTTP_200_OK,
)
@limiter.limit("3/minute")
async def send_otp(
    request: Request,
    payload: SendOTPRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session),
):
    otp = await AuthService.create_otp(db, payload.email)

    background_tasks.add_task(send_otp_email, payload.email, otp)

    return SendOTPResponse(message="OTP sent successfully")


@router.post(
    "/verify-otp",
    response_model=VerifyOTPResponse,
    status_code=status.HTTP_200_OK,
)
@limiter.limit("10/minute")
async def verify_otp(
    request: Request,
    payload: VerifyOTPRequest,
    db: AsyncSession = Depends(get_db_session),
):
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