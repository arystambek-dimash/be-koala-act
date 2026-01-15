from datetime import datetime, date
from typing import Optional, List

from pydantic import BaseModel

from src.app.constants import SubjectEnum


class UserRead(BaseModel):
    id: int
    email: str
    full_name: str
    current_score: int
    target_score: int
    exam_date: Optional[datetime] = None
    has_onboard: bool
    is_admin: bool = False

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    current_score: Optional[int] = None
    target_score: Optional[int] = None
    exam_date: Optional[datetime] = None


# --- Village schemas ---
class UserVillageRead(BaseModel):
    id: int
    village_id: int
    svg: Optional[str] = None
    subject: SubjectEnum
    treasure_amount: int
    last_collect_date: Optional[datetime] = None
    last_update_at: Optional[datetime] = None
    speed_production_treasure: int

    class Config:
        from_attributes = True


class UserCastleWithVillages(BaseModel):
    id: int
    svg: Optional[str] = None
    treasure_amount: int
    last_collect_date: Optional[datetime] = None
    taps_used_today: int
    last_tap_reset_date: Optional[date] = None
    speed_production_treasure: int
    villages: List[UserVillageRead]

    class Config:
        from_attributes = True
