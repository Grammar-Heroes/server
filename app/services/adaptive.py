from app.models.knowledge import KnowledgeProgress

# def select_worst_kc(kcs: list[KnowledgeProgress]) -> int | None:
#     if not kcs:
#         return None
    
#     # accuracy = correct / attempts
#     worst = min(kcs, key=lambda kc: kc.correct / kc.attempts if kc.attempts > 0 else 0)
#     return worst.kc_id

def select_worst_kc(kcs: list[KnowledgeProgress], eligible_kc_ids: list[int]) -> int | None:
    filtered = [kc for kc in kcs if kc.kc_id in eligible_kc_ids]
    if not filtered:
        return None
    worst = min(
        filtered,
        key=lambda kc: kc.correct / kc.attempts if kc.attempts > 0 else 0
    )

    return worst.kc_id