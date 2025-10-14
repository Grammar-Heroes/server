# app/routers/knowledge.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.db import get_db
from app.core.security import get_current_user
from app.schemas.knowledge import KnowledgeOut
from app.crud import knowledge as knowledge_crud

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

@router.get("/", response_model=List[KnowledgeOut])
async def get_user_knowledge(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Return all KnowledgeComponent (KC) progress for the authenticated user."""
    return await knowledge_crud.get_user_kcs(db, current_user.id)
