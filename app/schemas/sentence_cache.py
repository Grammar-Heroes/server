from pydantic import BaseModel
from typing import List

class SentenceCheckRequest(BaseModel):
    sentence: str

class SentenceCheckResponse(BaseModel):
    is_correct: bool
    error_indices: List[int]
    feedback: List[str]