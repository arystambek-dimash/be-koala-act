from typing import Optional, List

from pydantic import BaseModel, Field


class PassageNodeRead(BaseModel):
    id: int
    title: str
    content: str
    order_index: int


class PassageBossRead(BaseModel):
    id: int
    title: Optional[str] = Field(None, max_length=255)
    config: Optional[dict] = Field(None)
    pass_score: Optional[int] = Field(None, ge=0, le=100)
    reward_coins: Optional[int] = Field(None, ge=0)
    reward_xp: Optional[int] = Field(None, ge=0)
    node_id: Optional[int] = Field(None, ge=0)


class PassageRead(BaseModel):
    id: int
    title: str
    order_index: int
    boss: PassageBossRead


class RoadmapRead(BaseModel):
    passages: List[PassageRead]
