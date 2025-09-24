from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserOut(BaseModel):
    id: int
    firebase_uid: str
    email: Optional[str]
    display_name: Optional[str]
    grade_level: Optional[str]
    is_admin: bool
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    display_name: Optional[str]
    grade_level: Optional[str]


class NodeSeed(BaseModel):
    seed: str


class UserWithSeed(BaseModel):
    firebase_uid: str
    seed: str

    class Config:
        from_attributes = True
