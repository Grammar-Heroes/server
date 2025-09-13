from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.core.security import get_current_user
from app.schemas.progress import ProgressOut, LevelClearRequest
from app.crud import progress as progress_crud # might change to -> from app.crud import progress
from typing import List

router = APIRouter(prefix="/progress", tags=["progress"])

@router.get("/", response_model=List[ProgressOut])
async def get_all_progress(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return await progress_crud.get_progress(db, current_user.id)

# @router.post("/", response_model=ProgressOut)
# async def update_progress(payload: ProgressUpdate, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
#     return await crud.progress.set_progress(db, current_user.id, payload.level_id, payload.status)

@router.post("/clear", response_model=ProgressOut)
async def clear_level(payload: LevelClearRequest, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return await progress_crud.clear_level(db, current_user.id, payload.level_id)

# NOTES 
# Make sure get_current_user actually returns a User model (with .id).
# If it only returns a dict (from Firebase claims), you’ll get an attribute error.
# If it’s a dict, change to current_user["id"].