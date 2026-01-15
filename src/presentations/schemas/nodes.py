from typing import Optional, Dict, Any

from pydantic import BaseModel, Field


class PassageNodeCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: Optional[str] = None
    order_index: Optional[int] = Field(None, ge=0)
    config: Optional[Dict[str, Any]] = Field(default_factory=dict)
    pass_score: int = Field(..., ge=0)
    reward_coins: int = Field(..., ge=0)
    reward_xp: int = Field(..., ge=0)


class PassageNodeUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = None
    order_index: Optional[int] = Field(None, ge=0)


class BossNodeUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    pass_score: Optional[int] = Field(None, ge=0)
    reward_coins: Optional[int] = Field(None, ge=0)
    reward_xp: Optional[int] = Field(None, ge=0)


class NodeRead(BaseModel):
    id: int
    passage_id: int
    title: str
    content: Optional[str]
    order_index: int
    is_boss: bool
    config: Dict[str, Any] = Field(default_factory=dict)
    pass_score: Optional[int] = None
    reward_coins: Optional[int] = None
    reward_xp: Optional[int] = None

    class Config:
        from_attributes = True
