from fastapi import APIRouter, Depends
from app.schemas.gameplay import SubmissionCreate, SubmissionOut
from app.core.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_current_user
from app.services.grammar import check_sentence
from app.crud import submission as submission_crud
from app.crud import knowledge as knowledge_crud
import logging

logger = logging.getLogger("uvicorn")
logging.basicConfig(level=logging.INFO)

router = APIRouter(prefix="/gameplay", tags=["gameplay"])

@router.post("/submit", response_model=SubmissionOut)
async def submit_sentence(
    payload: SubmissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # 1️⃣ Check grammar (cached if available)
    feedback = await check_sentence(payload.sentence)
    is_correct = feedback["is_correct"]

    if feedback.get("from_cache", False):
        logger.info(f"[CACHE HIT] {payload.sentence}")
    else:
        logger.info(f"[CACHE MISS] {payload.sentence}")

    # 2️⃣ Update user's knowledge using BKT
    await knowledge_crud.update_knowledge(db, current_user.id, payload.kc_id, is_correct)

    # 3️⃣ Fetch updated p_know after update
    p_know = await knowledge_crud.get_knowledge_value(db, current_user.id, payload.kc_id)
    if p_know is None:
        p_know = 0.5  # fallback default

    # 4️⃣ Record submission
    submission = await submission_crud.create_submission(
        db,
        user_id=current_user.id,
        kc_id=payload.kc_id,
        sentence=payload.sentence,
        feedback=feedback
    )

    # 5️⃣ Return data (Unity will store p_know in GameData.currentPKnow)
    return {
        "is_correct": bool(submission.is_correct),
        "error_indices": submission.feedback.get("error_indices", []),
        "feedback": submission.feedback.get("feedback", []),
        "from_cache": feedback.get("from_cache", False),
        "p_know": float(p_know)
    }