from typing import Optional

from pydantic import BaseModel, Field


class PassageCreate(BaseModel):
    village_id: int
    title: str = Field(..., min_length=1, max_length=255)


class PassageUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)


class PassageReorder(BaseModel):
    passage_id: int
    new_index: int = Field(..., ge=1)


class PassageNodeRead(BaseModel):
    id: int
    title: str
    content: Optional[str] = None
    is_boss: bool = False

    class Config:
        from_attributes = True


class PassageRead(BaseModel):
    id: int
    title: str
    order_index: int

    class Config:
        from_attributes = True
