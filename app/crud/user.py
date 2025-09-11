from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from typing import Optional

async def get_by_firebase_uid(db: AsyncSession, firebase_uid: str) -> Optional[User]:
    q = select(User).where(User.firebase_uid == firebase_uid)
    result = await db.execute(q)
    return result.scalars().first()

async def get_by_id(db: AsyncSession, id: int) -> Optional[User]:
    q = select(User).where(User.id == id)
    result = await db.execute(q)
    return result.scalars().first()

async def create_from_firebase(db: AsyncSession, firebase_uid: str, email: str | None, display_name: str | None) -> User:
    user = User(firebase_uid=firebase_uid, email=email, display_name=display_name)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user