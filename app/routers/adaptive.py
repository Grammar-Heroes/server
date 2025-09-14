from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.core.security import get_current_user
from app.crud import knowledge as knowledge_crud
from app.services.adaptive import select_worst_kc
from app.schemas.adaptive import AdaptiveKCResponse

router = APIRouter(prefix="/adaptive", tags=["adaptive"])

@router.post("/next", response_model=AdaptiveKCResponse)
async def get_next_kc(
    eligible_kc_ids: list[int], # frontend will send eligible KCs
    db: AsyncSession = Depends(get_db), 
    current_user=Depends(get_current_user)
):
    kcs = await knowledge_crud.get_user_kcs(db, current_user.id)
    kc_id = select_worst_kc(kcs, eligible_kc_ids)
    return {"kc_id": kc_id}