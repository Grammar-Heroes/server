from sqlalchemy.ext.asyncio import AsyncSession
from app.models.submission import Submission

async def create_submission(db: AsyncSession, user_id: int, kc_id: int, sentence: str, feedback: dict):
    submission = Submission(
        user_id=user_id,
        kc_id=kc_id,
        sentence=sentence,
        is_correct=1 if feedback["is_correct"] else 0,
        feedback={"error_indices": feedback["error_indices"]}
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)
    return submission