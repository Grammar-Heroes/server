from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.core.security import get_current_user
from app.schemas.progress import ProgressOut, ProgressUpdate
from app import crud
from typing import List

router = APIRouter(prefix="/progress", tags=["progress"])

@router.get("/", response_model=List[ProgressOut])
async def get_all_progress(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return await crud.progress.get_progress(db, current_user.id)

@router.post("/", response_model=ProgressOut)
async def update_progress(payload: ProgressUpdate, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return await crud.progress.set_progress(db, current_user.id, payload.level_id, payload.status)