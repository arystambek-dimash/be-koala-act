from typing import Optional

from pydantic import BaseModel


class BuildingCreate(BaseModel):
    title: str
    svg: Optional[bytes] = None
    treasure_capacity: int = 300
    speed_production_treasure: int = 1
    cost: Optional[int] = None
    order_index: int = 1


class BuildingUpdate(BaseModel):
    title: Optional[str] = None
    svg: Optional[bytes] = None
    treasure_capacity: Optional[int] = None
    speed_production_treasure: Optional[int] = None
    cost: Optional[int] = None
    order_index: Optional[int] = None


class BuildingRead(BaseModel):
    id: int
    title: str
    svg: Optional[str] = None
    treasure_capacity: int
    speed_production_treasure: int
    cost: Optional[int] = None
    order_index: int

    class Config:
        orm_mode = True
