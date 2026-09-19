from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import hash_password
from app.models.role import Role
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


async def list_users(
    db: AsyncSession,
    *,
    skip: int = 0,
    limit: int = 50,
    search: str | None = None,
) -> tuple[list[User], int]:
    query = select(User).options(selectinload(User.role).selectinload(Role.permissions))

    if search:
        pattern = f"%{search.lower()}%"
        query = query.where(
            func.lower(User.email).like(pattern)
            | func.lower(User.nom).like(pattern)
            | func.lower(User.prenom).like(pattern)
        )

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    result = await db.execute(query.order_by(User.nom, User.prenom).offset(skip).limit(limit))
    return list(result.scalars().all()), total


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> User:
    result = await db.execute(
        select(User)
        .options(selectinload(User.role).selectinload(Role.permissions))
        .where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable")
    return user


async def create_user(db: AsyncSession, data: UserCreate) -> User:
    existing = await db.execute(select(User).where(User.email == data.email.lower()))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un compte existe déjà avec cet e-mail",
        )

    role_result = await db.execute(select(Role).where(Role.id == data.role_id))
    role = role_result.scalar_one_or_none()
    if role is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rôle invalide")

    user = User(
        email=data.email.lower(),
        password_hash=hash_password(data.password),
        nom=data.nom,
        prenom=data.prenom,
        telephone=data.telephone,
        role_id=data.role_id,
        is_active=data.is_active,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user, attribute_names=["role"])
    return await get_user_by_id(db, user.id)


async def update_user(db: AsyncSession, user_id: UUID, data: UserUpdate) -> User:
    user = await get_user_by_id(db, user_id)

    if data.email and data.email.lower() != user.email:
        existing = await db.execute(select(User).where(User.email == data.email.lower()))
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Un compte existe déjà avec cet e-mail",
            )
        user.email = data.email.lower()

    if data.nom is not None:
        user.nom = data.nom
    if data.prenom is not None:
        user.prenom = data.prenom
    if data.telephone is not None:
        user.telephone = data.telephone
    if data.role_id is not None:
        role_result = await db.execute(select(Role).where(Role.id == data.role_id))
        if role_result.scalar_one_or_none() is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rôle invalide")
        user.role_id = data.role_id
    if data.is_active is not None:
        user.is_active = data.is_active
    if data.password:
        user.password_hash = hash_password(data.password)
        user.failed_login_attempts = 0
        user.locked_until = None

    await db.flush()
    return await get_user_by_id(db, user.id)


async def deactivate_user(db: AsyncSession, user_id: UUID) -> User:
    user = await get_user_by_id(db, user_id)
    user.is_active = False
    await db.flush()
    return user
