from typing import Optional, Dict, Any, List

from pydantic import BaseModel, Field

from src.presentations.schemas.questions import QuestionRead


class PassageNodeCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: Optional[str] = None
    config: Optional[Dict[str, Any]] = Field(default_factory=dict)


class PassageNodeUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class BossNodeCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: Optional[str] = None
    config: Optional[Dict[str, Any]] = Field(default_factory=dict)
    pass_score: int = Field(..., ge=0)
    reward_coins: int = Field(..., ge=0)
    reward_xp: int = Field(..., ge=0)
    passage_id: int = Field(..., ge=0)


class BossNodeUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    pass_score: Optional[int] = Field(None, ge=0)
    reward_coins: Optional[int] = Field(None, ge=0)
    reward_xp: Optional[int] = Field(None, ge=0)


class NodeDetailedRead(BaseModel):
    id: int
    passage_id: int
    title: str
    content: Optional[str]
    is_boss: bool
    config: dict
    pass_score: Optional[int]
    reward_coins: Optional[int]
    reward_xp: Optional[int]
    questions: List[QuestionRead] = []

    class Config:
        from_attributes = True


class BossNodeRead(BaseModel):
    id: int
    passage_id: int
    title: str
    content: Optional[str]
    is_boss: bool = True
    config: Dict[str, Any] = Field(default_factory=dict)
    pass_score: int
    reward_coins: int
    reward_xp: int

    class Config:
        from_attributes = True
