from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserUpdate
from typing import Optional


async def get_by_firebase_uid(db: AsyncSession, firebase_uid: str) -> Optional[User]:
    q = select(User).where(User.firebase_uid == firebase_uid)
    result = await db.execute(q)
    return result.scalars().first()


async def get_by_id(db: AsyncSession, id: int) -> Optional[User]:
    q = select(User).where(User.id == id)
    result = await db.execute(q)
    return result.scalars().first()


async def create_from_firebase(db: AsyncSession, uid: str, email: str, name: str | None):
    if not name:  # fallback if Firebase doesn't provide one
        name = email.split("@")[0]  # e.g., use prefix of email
        # or just name = "Player"

    new_user = User(
        firebase_uid=uid,
        email=email,
        display_name=name,
        grade_level=None,  # will be set later via profile completion
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_user(db: AsyncSession, user: User, updates: UserUpdate) -> User:
    for field, value in updates.dict(exclude_unset=True).items():  # (model_dump in Pydantic v2)
        setattr(user, field, value)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
