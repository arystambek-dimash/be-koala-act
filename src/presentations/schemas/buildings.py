from typing import Optional, List

from pydantic import BaseModel

from src.app.constants import BuildingType
from src.presentations.schemas.passages import PassageRead


class BuildingCreate(BaseModel):
    title: str
    type: BuildingType
    svg: Optional[bytes] = None
    treasure_capacity: int = 300
    speed_production_treasure: int = 1
    cost: Optional[int] = None
    order_index: int = 1


class BuildingUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[BuildingType] = None
    svg: Optional[bytes] = None
    treasure_capacity: Optional[int] = None
    speed_production_treasure: Optional[int] = None
    cost: Optional[int] = None
    order_index: Optional[int] = None


class BuildingRead(BaseModel):
    id: int
    title: str
    type: BuildingType
    svg: Optional[str] = None
    treasure_capacity: int
    speed_production_treasure: int
    cost: Optional[int] = None
    order_index: int

    class Config:
        from_attributes = True


class BuildingWithPassagesRead(BaseModel):
    id: int
    title: str
    type: BuildingType
    svg: Optional[str] = None
    treasure_capacity: int
    speed_production_treasure: int
    cost: Optional[int] = None
    order_index: int

    passages: List[PassageRead]

    class Config:
        from_attributes = True
