from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.db import get_db
from app.core.security import get_current_user
from app.schemas.inventory import InventoryOut, InventoryAddRequest
from app.crud import inventory as inventory_crud

router = APIRouter(prefix="/inventory", tags=["inventory"])

@router.get("/", response_model=List[InventoryOut])
async def get_inventory(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return await inventory_crud.get_inventory(db, current_user.id)

@router.post("/add", response_model=InventoryOut)
async def add_inventory_item(payload: InventoryAddRequest, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return await inventory_crud.add_item(db, current_user.id, payload.item_id)