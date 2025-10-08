from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.core.security import get_current_user
from app.schemas.adventure import AdventureCreate, AdventureOut, AdventureUpdate
from app.crud import adventure as adventure_crud
from app.models.user import User
import uuid

router = APIRouter(prefix="/adventure", tags=["adventure"])

@router.get("/current", response_model=AdventureOut)
async def get_current_adventure(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the user's current adventure."""
    adventure = await adventure_crud.get_user_adventure(db, current_user.id)
    if not adventure:
        raise HTTPException(status_code=404, detail="No active adventure found")
    return adventure

@router.post("/", response_model=AdventureOut)
async def create_new_adventure(
    adventure: AdventureCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new adventure."""
    # check if user already has an active adventure
    existing = await adventure_crud.get_user_adventure(db, current_user.id)
    if existing:
        raise HTTPException( 
            status_code=400,
            detail="User already has an active adventuure"
        )
    return await adventure_crud.create_adventure(db, current_user.id, adventure)

@router.patch("/current", response_model=AdventureOut)
async def update_current_adventure(
    updates: AdventureUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update the current adventure."""
    adventure = await adventure_crud.get_user_adventure(db, current_user.id)
    if not adventure:
        raise HTTPException(status_code=404, detail="No active adventure found")
    return await adventure_crud.update_adventure(db, adventure, updates)

@router.delete("/current")
async def delete_current_adventure(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete the current adventure."""
    adventure = await adventure_crud.get_user_adventure(db, current_user.id)
    if not adventure:
        raise HTTPException(status_code=404, detail="No active adventure found")
    
    await adventure_crud.delete_adventure(db, adventure)
    return {"message": "Adventure deleted successfully"}