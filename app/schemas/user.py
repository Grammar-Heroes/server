from pydantic import BaseModel
from datetime import datetime

class UserOut(BaseModel):
    id: int
    firebase_uid: str
    email: str | None
    display_name: str | None
    is_admin: bool
    created_at: datetime | None

    class Config:
        # before: orm_mode = True
        from_attributes = True

class NodeSeed(BaseModel):
    seed: str

class UserWithSeed(BaseModel):
    firebase_uid: str
    seed: str

    class Config:
        from_attributes = True