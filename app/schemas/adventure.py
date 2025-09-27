from pydantic import BaseModel
from datetime import datetime
from typing import List

class AdventureBase(BaseModel):
    adventure_id: str
    items_collected: List[str] = []
    cleared_nodes: List[str] = []
    current_adaptive_kc: str | None = None
    enemy_level: int = 1
    enemy_writing_level: int = 1
    enemy_defense_level: int = 1
    player_level: int = 1
    writing_level: int = 1
    defense_level: int = 1
    current_floor: int = 1

class AdventureCreate(AdventureBase):
    pass 

class AdventureUpdate(BaseModel):
    items_collected: List[str] | None = None
    cleared_nodes: List[str] | None = None
    current_adaptive_kc: str | None = None
    enemy_level: int | None = None
    enemey_writing_level: int | None = None
    enemy_defense_level: int | None = None
    player_level: int | None = None
    writing_level: int | None = None
    defense_level: int | None = None
    current_floor: int | None = None

class AdventureOut(AdventureBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True