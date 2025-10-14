from typing import List, Optional

from pydantic import BaseModel


class SubmissionCreate(BaseModel):
    sentence: str
    kc_id: int


class CandidateFeedback(BaseModel):
    text: str
    language_tool_matches: int
    acceptability: Optional[float] = None


class ScoreSummary(BaseModel):
    language_tool_matches: int
    acceptability: Optional[float] = None
    semantic: Optional[float] = None
    perplexity: Optional[float] = None
    kc_alignment: Optional[float] = None


class SubmissionOut(BaseModel):
    is_correct: bool
    error_indices: List[int]
    feedback: List[str]
    scores: Optional[ScoreSummary] = None
    best_candidate: Optional[str] = None
    candidates: List[CandidateFeedback] = []
    from_cache: bool = False
    p_know: Optional[float] = None  # <-- add this line

    class Config:
        from_attributes = True

