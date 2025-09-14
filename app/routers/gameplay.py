from fastapi import APIRouter, Depends
from app.schemas.gameplay import SubmissionCreate, SubmissionOut
from app.core.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_current_user
from app.services import grammar
from app.crud import submission as submission_crud # to avoid variable clashing
from app.services.grammar import check_sentence
from app.crud import knowledge as knowledge_crud

router = APIRouter(prefix="/gameplay", tags=["gameplay"])

@router.post("/submit", response_model=SubmissionOut)
async def submit_sentence(
    payload: SubmissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    feedback = await check_sentence(payload.sentence)
    is_correct = feedback["is_correct"]

    await knowledge_crud.update_knowledge(db, current_user.id, payload.kc_id, is_correct)

    submission = await submission_crud.create_submission(
        db,
        user_id=current_user.id,
        kc_id=payload.kc_id,
        sentence=payload.sentence,
        feedback=feedback,
    )
    return {
        "is_correct": bool(submission.is_correct),
        "error_indices": submission.feedback.get("error_indices", [])
    }

async def submit_submission(payload: SubmissionCreate, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):

    #grammar
    corrected, issues = grammar.check_sentence(payload.sentence)

    # naive scoring: higher issues => lower score (0..100)
    # score = max(0, int(round((1 - min(1.0, issues * 0.2)) * 100)))

    # Create submission row (crud.submission should be implemented)
    # For now we just return the core response and sketch how to update BKT:
    # - fetch user's prior mastery on kc_id (crud.progress.get_user_kc)
    # - update using bkt.update_bkt
    # - store back to DB

    # PSEUDO (you'll implement crud.progress functions similarly to crud.user):
    # prior = await crud.progress.get_mastery(db, current_user.id, payload.kc_id) or 0.2
    # next_prior = bkt.update_bkt(prior, is_correct=(score>70))
    # await crud.progress.set_mastery(db, current_user.id, payload.kc_id, next_prior)

    return {
        "original": payload.sentence,
        "corrected": corrected,
        "issues_found": issues,
        # "score": score,
        "kc_id": payload.kc_id
    }