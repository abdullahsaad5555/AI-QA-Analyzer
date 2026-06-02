# app/schemas/auth.py

from pydantic import BaseModel, EmailStr, Field


class SendOTPRequest(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")


class SendOTPResponse(BaseModel):
    message: str = Field(..., example="OTP sent successfully")


class VerifyOTPRequest(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    otp: str = Field(..., min_length=4, max_length=10, example="123456")


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthUserResponse(BaseModel):
    id: str
    email: EmailStr

    class Config:
        from_attributes = True


class VerifyOTPResponse(BaseModel):
    message: str = "Login successful"
    user: AuthUserResponse
    tokens: TokenResponse
