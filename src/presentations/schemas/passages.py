from typing import Optional, List

from pydantic import BaseModel, Field

from src.app.constants import SubjectEnum


class PassageCreate(BaseModel):
    village_id: int
    subject: SubjectEnum
    title: str = Field(..., min_length=1, max_length=255)
    order_index: int = Field(default=1, ge=0)


class PassageUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    order_index: Optional[int] = Field(None, ge=0)
    subject: Optional[SubjectEnum] = None


class PassageNodeRead(BaseModel):
    id: int
    title: str
    content: Optional[str] = None
    order_index: int
    is_boss: bool = True

    class Config:
        from_attributes = True


class PassageRead(BaseModel):
    id: int
    subject: SubjectEnum
    title: str
    order_index: int

    class Config:
        from_attributes = True
