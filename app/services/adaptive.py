from app.models.knowledge import KnowledgeProgress

def select_worst_kc(kcs: list[KnowledgeProgress], eligible_kc_ids: list[int]) -> int | None:
    filtered = [kc for kc in kcs if kc.kc_id in eligible_kc_ids]
    if not filtered:
        return None
    worst = min(
        filtered,
        key=lambda kc: kc.p_know
    )
    return worst.kc_id