from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserRead(BaseModel):
    id: int
    email: str
    full_name: str
    current_score: int
    target_score: int
    exam_date: datetime
    has_onboard: bool

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    current_score: Optional[int] = None
    target_score: Optional[int] = None
    exam_date: Optional[datetime] = None
