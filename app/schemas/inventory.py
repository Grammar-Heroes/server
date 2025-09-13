from pydantic import BaseModel
from datetime import datetime

class InventoryAddRequest(BaseModel):
    item_id: str

class InventoryOut(BaseModel):
    item_id: str
    obtained_at: datetime

    class Config:
        from_attributes = True