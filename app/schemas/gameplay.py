from pydantic import BaseModel

class SubmissionCreate(BaseModel):
    sentence: str
    kc_id: int

