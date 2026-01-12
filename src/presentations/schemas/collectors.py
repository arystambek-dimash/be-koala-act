from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.app.constants import FundType, SubjectEnum


class TreasureStatus(BaseModel):
    current_amount: int
    capacity: int
    production_rate: int  # per hour
    last_collect_date: Optional[datetime]
    time_to_full_minutes: int
    fund_type: FundType


class CastleStatus(BaseModel):
    castle_id: int
    castle_title: str
    treasure: TreasureStatus
    taps_remaining: int
    max_taps_per_day: int
    coins_per_tap: int


class VillageStatus(BaseModel):
    village_id: int
    village_title: str
    subject: SubjectEnum
    treasure: TreasureStatus


class CollectResult(BaseModel):
    collected_amount: int
    fund_type: FundType
    new_wallet_balance: int


class TapResult(BaseModel):
    coins_collected: int
    taps_remaining: int
    new_wallet_balance: int


class UpgradeInfo(BaseModel):
    can_upgrade: bool
    current_level: int
    next_level: Optional[int]
    upgrade_cost: Optional[int]
    cost_fund_type: FundType
    current_balance: int
    reason: Optional[str] = None


class UpgradeResult(BaseModel):
    success: bool
    new_level: int
    cost_paid: int
    new_balance: int
