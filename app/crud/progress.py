from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.models.progress import Progress

async def get_progress(db: AsyncSession, user_id: int) -> List[Progress]:
    q = select(Progress).where(Progress.user_id == user_id)
    res = await db.execute(q)
    return res.scalars().all()

async def get_level_progress(db: AsyncSession, user_id: int, level_id: str) -> Optional[Progress]:
    q = select(Progress).where(
        Progress.user_id == user_id, Progress.level_id == level_id
    )
    res = await db.execute(q)
    return res.scalars().first()

async def set_progress(db: AsyncSession, user_id: int, level_id: str, status: str) -> Progress:
    progress = await get_level_progress(db, user_id, level_id)
    if progress:
        progress.status = status
    else:
        progress = Progress(user_id=user_id, level_id=level_id, status=status)
        db.add(progress)
    await db.commit()
    await db.refresh(progress)
    return progress