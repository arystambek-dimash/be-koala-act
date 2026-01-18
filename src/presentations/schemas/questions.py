from typing import List, Optional, Any, Literal

from pydantic import BaseModel, Field

from src.app.constants import QuestionType


class FindErrorContent(BaseModel):
    sentence: str
    error_index: int
    correct_word: str
    explanation: str


class StrikeOutContent(BaseModel):
    sentence: str
    correct_ids_to_remove: List[int]
    explanation: str


class OrderingItem(BaseModel):
    id: str
    content: str


class OrderingContent(BaseModel):
    items: List[OrderingItem]
    correct_order: List[str]
    explanation: str


class HighlightContent(BaseModel):
    passage: str
    question: str
    correct_phrase: str
    explanation: str


class SwipeLabels(BaseModel):
    left: str
    right: str


class SwipeDecisionContent(BaseModel):
    content: str
    correct_swipe: Literal["left", "right"]
    explanation: str
    labels: SwipeLabels


class MultipleChoiceOption(BaseModel):
    id: str
    text: str
    is_correct: bool


class MultipleChoiceContent(BaseModel):
    question: str
    options: List[MultipleChoiceOption]
    explanation: str


class FillGapContent(BaseModel):
    question: str
    correct_answer: str
    explanation: str


class MatchingPair(BaseModel):
    left: str
    right: str


class MatchingContent(BaseModel):
    pairs: List[MatchingPair]


class GraphPointContent(BaseModel):
    graph_description: str
    target_x: float
    target_y: float
    radius: float = Field(default=15)
    explanation: str


class TrendArrowContent(BaseModel):
    question: str
    correct_trend: Literal["increase", "decrease", "constant"]
    explanation: str


class SliderValueContent(BaseModel):
    image_description: str
    question: str
    min_value: float
    max_value: float
    correct_value: float
    tolerance: float
    unit: str
    explanation: str


# --- Question schemas ---
class QuestionBase(BaseModel):
    type: QuestionType
    text: str = Field(..., description="Question prompt text")
    content: dict[str, Any]


class QuestionCreate(BaseModel):
    type: QuestionType
    content: dict[str, Any]


class QuestionUpdate(BaseModel):
    type: Optional[QuestionType] = None
    content: Optional[dict[str, Any]] = None


class QuestionRead(BaseModel):
    id: int
    node_id: int
    type: str
    content: dict[str, Any]
    order_index: Optional[int] = None

    class Config:
        from_attributes = True


class QuestionReorder(BaseModel):
    question_id: int
    order_index: int
