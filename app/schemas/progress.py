from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict

class NodeSeeds(BaseModel):
    floor1: str | None = None
    floor2: str | None = None
    floor3: str | None = None

class ProgressOut(BaseModel):
    level_id: str
    status: str
    updated_at: datetime

    class Config:
        from_attributes = True

class ProgressUpdate(BaseModel):
    level_id: str
    status: str