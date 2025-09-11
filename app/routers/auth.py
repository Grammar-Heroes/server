from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.schemas.user import UserOut
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/me", response_model=UserOut)
async def me(current_user = Depends(get_current_user)):
    return current_user