from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, Field

from src.app.constants import SubjectEnum


class UserLevel(str, Enum):
    WEAK = "weak"
    STRONG = "strong"
    KNOW_NOT_GOOD = "know_not_good"
    NO_IDEA = "no_idea"


class PassageOnboard(BaseModel):
    passage_id: int
    user_level: UserLevel


class SubjectOnboard(BaseModel):
    subject: SubjectEnum
    passages: List[PassageOnboard]


class OnboardCreate(BaseModel):
    current_score: int = Field(..., ge=0, le=1600)
    target_score: int = Field(..., ge=0, le=1600)
    exam_date: datetime
    subjects: List[SubjectOnboard] = Field(..., min_length=1)


class SingleSubjectOnboard(BaseModel):
    subject: SubjectEnum
    passages: List[PassageOnboard] = Field(..., min_length=1)


class PassageOnboardPreview(BaseModel):
    id: int
    title: str
    order_index: int
    subject: SubjectEnum

    class Config:
        from_attributes = True
