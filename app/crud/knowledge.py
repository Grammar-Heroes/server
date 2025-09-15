from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.services.bkt import update_bkt
from app.models.knowledge import KnowledgeProgress

async def update_knowledge(db: AsyncSession, user_id: int, kc_id: int, is_correct: bool):
    q = select(KnowledgeProgress).where(
        KnowledgeProgress.user_id == user_id,
        KnowledgeProgress.kc_id == kc_id
    )
    res = await db.execute(q)
    kp = res.scalars().first()

    if kp:
        kp.attempts += 1
        if is_correct:
            kp.correct += 1

    # use stored slip, guess, transit
        kp.p_know = update_bkt(kp.p_know, is_correct, kp.slip, kp.guess, kp.transit)

    else:
        kp = KnowledgeProgress(
            user_id=user_id,
            kc_id=kc_id,
            attempts=1,
            correct=1 if is_correct else 0,
            p_know=update_bkt(0.2, is_correct, 0.1, 0.2, 0.15),
            slip=0.1,
            guess=0.2,
            transit=0.15
        )
        db.add(kp)

    await db.commit()
    await db.refresh(kp)
    return kp

async def get_user_kcs(db: AsyncSession, user_id: int):
    q = select(KnowledgeProgress).where(
        KnowledgeProgress.user_id == user_id
    )
    res = await db.execute(q)
    return res.scalars().all()