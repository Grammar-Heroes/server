from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.core.security import get_current_user
from app.schemas.user import UserOut, UserUpdate
from app.models.user import User
from app import crud
from pydantic import BaseModel

router = APIRouter(prefix="/users", tags=["users"])

# --- Existing endpoints ---
@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.patch("/me", response_model=UserOut)
async def update_me(
    updates: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):    
    return await crud.user.update_user(db, current_user, updates)

# --- Username check endpoint ---
@router.get("/check-username")
async def check_username(display_name: str = Query(...), db: AsyncSession = Depends(get_db)):
    q = select(User).where(User.display_name == display_name)
    result = await db.execute(q)
    exists = result.scalars().first() is not None
    return {"is_unique": not exists}

# --- Update display name endpoint ---
class DisplayNameUpdate(BaseModel):
    display_name: str

@router.patch("/me/display-name")
async def update_display_name(
    payload: DisplayNameUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check uniqueness
    existing = await db.scalar(select(User).where(User.display_name == payload.display_name))
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Update and commit
    current_user.display_name = payload.display_name
    await db.commit()
    await db.refresh(current_user)

    return {"display_name": current_user.display_name}