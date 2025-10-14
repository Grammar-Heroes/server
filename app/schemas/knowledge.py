# app/schemas/knowledge.py
from pydantic import BaseModel

class KnowledgeOut(BaseModel):
    kc_id: int
    p_know: float
    slip: float
    guess: float
    transit: float
    attempts: int
    correct: int

    class Config:
        from_attributes = True
