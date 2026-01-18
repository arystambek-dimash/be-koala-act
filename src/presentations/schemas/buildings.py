from typing import Optional, List

from pydantic import BaseModel

from src.app.constants import BuildingType, SubjectEnum
from src.presentations.schemas.passages import PassageRead


class BuildingCastleCreate(BaseModel):
    title: str
    type: BuildingType
    svg: Optional[bytes] = None
    treasure_capacity: int = 300
    speed_production_treasure: int = 1
    cost: Optional[int] = None
    next_building_id: Optional[int] = None


class BuildingVillageCreate(BuildingCastleCreate):
    subject: SubjectEnum
    next_building_id: Optional[int] = None


class BuildingUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[BuildingType] = None
    svg: Optional[bytes] = None
    treasure_capacity: Optional[int] = None
    speed_production_treasure: Optional[int] = None
    cost: Optional[int] = None
    subject: Optional[SubjectEnum] = None


class BuildingCastleRead(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = None
    svg: Optional[str] = None
    treasure_capacity: Optional[int] = None
    speed_production_treasure: Optional[int] = None
    cost: Optional[int] = None
    next_building_id: Optional[int] = None

    class Config:
        from_attributes = True


class BuildingVillageRead(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = None
    svg: Optional[str] = None
    treasure_capacity: Optional[int] = None
    speed_production_treasure: Optional[int] = None
    cost: Optional[int] = None
    subject: Optional[SubjectEnum] = None
    next_building_id: Optional[int] = None

    class Config:
        from_attributes = True


class BuildingCastleUserRead(BuildingCastleRead):
    is_current: Optional[bool] = False

    class Config:
        from_attributes = True


class BuildingVillageUserRead(BuildingVillageRead):
    is_current: Optional[bool] = False

    class Config:
        from_attributes = True


class BuildingDetailedRead(BaseModel):
    id: Optional[int] = None
    building_id: Optional[int] = None
    title: Optional[str] = None
    building_title: Optional[str] = None
    type: Optional[BuildingType] = None
    svg: Optional[str] = None
    building_svg: Optional[str] = None
    treasure_capacity: Optional[int] = None
    speed_production_treasure: Optional[int] = None
    cost: Optional[int] = None
    subject: Optional[SubjectEnum] = None
    is_current: Optional[bool] = None
    next_building_id: Optional[int] = None

    class Config:
        from_attributes = True


class BuildingWithPassagesRead(BuildingDetailedRead):
    passages: List[PassageRead]

    class Config:
        from_attributes = True
