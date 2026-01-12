from typing import Optional

from pydantic import BaseModel, Field


class PassageCreate(BaseModel):
    village_id: int
    title: str = Field(..., min_length=1, max_length=255)
    order_index: int = Field(default=1, ge=0)


class PassageUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    order_index: Optional[int] = Field(None, ge=0)
