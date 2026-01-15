from typing import Optional, List

from pydantic import BaseModel, Field


class RoadmapNodeRead(BaseModel):
    id: int
    title: str
    content: Optional[str]
    order_index: int
    is_locked: bool
    is_completed: bool


class RoadmapBossRead(BaseModel):
    id: int
    title: Optional[str] = Field(None)
    content: Optional[str] = Field(None)
    config: Optional[dict] = Field(None)
    pass_score: Optional[int] = Field(None)
    reward_coins: Optional[int] = Field(None)
    reward_xp: Optional[int] = Field(None)
    is_locked: bool


class RoadmapPassageRead(BaseModel):
    id: int
    order_index: int
    title: str
    nodes: List[RoadmapNodeRead]
    boss: Optional[RoadmapBossRead] = None


class RoadmapRead(BaseModel):
    passages: List[RoadmapPassageRead]
