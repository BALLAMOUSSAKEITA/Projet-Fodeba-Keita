from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., examples=["admin@fodebakeita.gn"])
    password: str = Field(..., min_length=4, examples=["admin123"])


class UserInfo(BaseModel):
    id: UUID
    email: EmailStr
    nom: str
    prenom: str
    role: str
    permissions: list[str] = []

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserInfo


class RefreshRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    message: str
    reset_token: str | None = None


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)


class LoginLogResponse(BaseModel):
    id: UUID
    email: str
    success: bool
    ip_address: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
