from pydantic import BaseModel
from typing import List
from datetime import datetime

class SubmissionCreate(BaseModel):
    sentence: str
    kc_id: int

class SubmissionOut(BaseModel):
    is_correct: bool
    error_indices: List[int]

    class Config:
        from_attributes = True