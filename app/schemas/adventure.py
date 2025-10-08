from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional


class AdventureBase(BaseModel):
    adventure_id: str
    items_collected: List[str] = []
    cleared_nodes: List[str] = []
    current_adaptive_kc: Optional[str] = None

    # Stats / Levels
    enemy_level: int = 1
    enemy_writing_level: int = 1
    enemy_defense_level: int = 1
    player_level: int = 1
    writing_level: int = 1
    defense_level: int = 1
    current_floor: int = 1


class AdventureCreate(AdventureBase):
    """Used when creating a new adventure."""
    pass


class AdventureUpdate(BaseModel):
    """Used for PATCH /adventure/current — all fields optional."""
    items_collected: Optional[List[str]] = None
    cleared_nodes: Optional[List[str]] = None
    current_adaptive_kc: Optional[str] = None
    enemy_level: Optional[int] = None
    enemy_writing_level: Optional[int] = None
    enemy_defense_level: Optional[int] = None
    player_level: Optional[int] = None
    writing_level: Optional[int] = None
    defense_level: Optional[int] = None
    current_floor: Optional[int] = None


class AdventureOut(AdventureBase):
    """Response model for reading adventures."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)  # For Pydantic v2
