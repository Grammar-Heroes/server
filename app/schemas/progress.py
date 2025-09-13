from pydantic import BaseModel
from datetime import datetime

class LevelClearRequest(BaseModel):
    level_id: str

class ProgressOut(BaseModel):
    level_id: str
    cleared_at: datetime

    class Config:
        from_attributes = True