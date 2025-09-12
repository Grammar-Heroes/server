from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.core.security import get_current_user
from app.schemas.progress import NodeSeeds
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/node_structure", response_model=NodeSeeds)
async def get_node_structure(current_user: User = Depends(get_current_user)):
    return current_user.node_structure_seeds

@router.post("/node_structure", response_model=NodeSeeds)
async def set_node_structure(payload: NodeSeeds, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    current_user.node_structure_seeds = payload.dict() # use model_dump instead
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user.node_structure_seeds



    
