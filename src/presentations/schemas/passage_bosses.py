from typing import Optional

from pydantic import BaseModel, Field


class PassageBossCreate(BaseModel):
    passage_id: int
    node_id: int
    title: str = Field(default="Boss", max_length=255)
    config: dict = Field(default_factory=dict)
    pass_score: int = Field(default=70, ge=0, le=100)
    reward_coins: int = Field(default=50, ge=0)
    reward_xp: int = Field(default=100, ge=0)


class PassageBossUpdate(BaseModel):
    node_id: Optional[int] = Field(None, ge=0)
    title: Optional[str] = Field(None, max_length=255)
    config: Optional[dict] = None
    pass_score: Optional[int] = Field(None, ge=0, le=100)
    reward_coins: Optional[int] = Field(None, ge=0)
    reward_xp: Optional[int] = Field(None, ge=0)
