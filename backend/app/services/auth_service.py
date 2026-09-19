from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    generate_reset_token,
    hash_password,
    verify_password,
    verify_token,
)
from app.models.login_log import LoginLog
from app.models.role import Role
from app.models.user import User


async def log_login_attempt(
    db: AsyncSession,
    *,
    email: str,
    success: bool,
    user_id: UUID | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> None:
    db.add(
        LoginLog(
            user_id=user_id,
            email=email.lower(),
            success=success,
            ip_address=ip_address,
            user_agent=user_agent,
        )
    )


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(
        select(User)
        .options(selectinload(User.role).selectinload(Role.permissions))
        .where(User.email == email.lower())
    )
    return result.scalar_one_or_none()


async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> User:
    user = await get_user_by_email(db, email)

    if user is None or not user.is_active:
        await log_login_attempt(
            db,
            email=email,
            success=False,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants incorrects",
        )

    if user.is_locked:
        await log_login_attempt(
            db,
            email=email,
            success=False,
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte temporairement verrouillé. Réessayez plus tard.",
        )

    if not verify_password(password, user.password_hash):
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
            user.locked_until = datetime.now(UTC) + timedelta(
                minutes=settings.LOCKOUT_DURATION_MINUTES
            )
        await log_login_attempt(
            db,
            email=email,
            success=False,
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await db.flush()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants incorrects",
        )

    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login_at = datetime.now(UTC)
    await log_login_attempt(
        db,
        email=email,
        success=True,
        user_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return user


def build_token_response(user: User) -> dict:
    permissions = [p.code for p in user.role.permissions]
    return {
        "access_token": create_access_token(str(user.id), {"role": user.role.code}),
        "refresh_token": create_refresh_token(str(user.id)),
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": user,
        "permissions": permissions,
    }


async def refresh_access_token(db: AsyncSession, refresh_token: str) -> dict:
    user_id = verify_token(refresh_token, expected_type="refresh")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token invalide ou expiré",
        )

    result = await db.execute(
        select(User)
        .options(selectinload(User.role).selectinload(Role.permissions))
        .where(User.id == UUID(user_id), User.is_active.is_(True))
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur introuvable",
        )

    return build_token_response(user)


async def request_password_reset(db: AsyncSession, email: str) -> str | None:
    user = await get_user_by_email(db, email)
    if user is None:
        return None

    token = generate_reset_token()
    user.password_reset_token = token
    user.password_reset_expires = datetime.now(UTC) + timedelta(
        minutes=settings.PASSWORD_RESET_EXPIRE_MINUTES
    )
    await db.flush()
    return token


async def reset_password(db: AsyncSession, token: str, new_password: str) -> None:
    result = await db.execute(
        select(User).where(
            User.password_reset_token == token,
            User.password_reset_expires > datetime.now(UTC),
        )
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lien de réinitialisation invalide ou expiré",
        )

    user.password_hash = hash_password(new_password)
    user.password_reset_token = None
    user.password_reset_expires = None
    user.failed_login_attempts = 0
    user.locked_until = None
    await db.flush()
