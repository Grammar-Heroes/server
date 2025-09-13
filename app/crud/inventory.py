from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.inventory import InventoryItem

async def get_inventory(db: AsyncSession, user_id: int):
    q = select(InventoryItem).where(InventoryItem.user_id == user_id)
    res = await db.execute(q)
    return res.scalars().all()

async def add_item(db: AsyncSession, user_id: int, item_id: str):
    item = InventoryItem(user_id=user_id, item_id=item_id)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item