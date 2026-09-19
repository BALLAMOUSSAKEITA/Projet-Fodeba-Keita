from fastapi import APIRouter, Depends, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user, require_permission
from app.models.login_log import LoginLog
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginLogResponse,
    LoginRequest,
    LoginResponse,
    RefreshRequest,
    ResetPasswordRequest,
    UserInfo,
)
from app.schemas.common import MessageResponse
from app.services import auth_service

router = APIRouter()


def user_to_info(user: User) -> UserInfo:
    return UserInfo(
        id=user.id,
        email=user.email,
        nom=user.nom,
        prenom=user.prenom,
        role=user.role.code,
        permissions=[p.code for p in user.role.permissions],
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    credentials: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    user = await auth_service.authenticate_user(
        db,
        credentials.email,
        credentials.password,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    tokens = auth_service.build_token_response(user)
    return LoginResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        expires_in=tokens["expires_in"],
        user=user_to_info(user),
    )


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    tokens = await auth_service.refresh_access_token(db, body.refresh_token)
    return LoginResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        expires_in=tokens["expires_in"],
        user=user_to_info(tokens["user"]),
    )


@router.get("/me", response_model=UserInfo)
async def get_me(current_user: User = Depends(get_current_user)) -> UserInfo:
    return user_to_info(current_user)


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(
    body: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> ForgotPasswordResponse:
    token = await auth_service.request_password_reset(db, body.email)
    response = ForgotPasswordResponse(
        message="Si un compte existe, un lien de réinitialisation a été envoyé.",
    )
    if token and settings.ENVIRONMENT == "development":
        response.reset_token = token
    return response


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    body: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    await auth_service.reset_password(db, body.token, body.new_password)
    return MessageResponse(message="Mot de passe réinitialisé avec succès")


@router.get("/login-logs", response_model=list[LoginLogResponse])
async def list_login_logs(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("users.manage")),
) -> list[LoginLogResponse]:
    result = await db.execute(
        select(LoginLog).order_by(LoginLog.created_at.desc()).limit(min(limit, 200))
    )
    return list(result.scalars().all())
