from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.adventure import Adventure
from app.schemas.adventure import AdventureCreate, AdventureUpdate
from typing import Optional

async def get_user_adventure(db: AsyncSession, user_id: int) -> Optional[Adventure]:
    """Get the user's current adventure."""
    q = select(Adventure).where(Adventure.user_id == user_id)
    result = await db.execute(q)
    return result.scalar_one_or_none()

async def create_adventure(
        db: AsyncSession,
        user_id: int,
        adventure: AdventureCreate
) -> Adventure:
    """Create a new adventure for the user."""
    db_adventure = Adventure(
        user_id=user_id,
        # Avoid passing None/omitted fields so SQLAlchemy defaults can apply
        **adventure.model_dump(exclude_unset=True, exclude_none=True)
    )
    db.add(db_adventure)
    await db.commit()
    await db.refresh(db_adventure)
    return db_adventure

async def update_adventure(
        db: AsyncSession,
        db_adventure: Adventure,
        updates: AdventureUpdate
) -> Adventure:
    """Update an existing adventure."""
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(db_adventure, field, value)
    
    db.add(db_adventure)
    await db.commit()
    await db.refresh(db_adventure)
    return db_adventure
 
async def delete_adventure(db: AsyncSession, adventure: Adventure) -> None:
    """Delete an adventure."""
    await db.delete(adventure)
    await db.commit()
