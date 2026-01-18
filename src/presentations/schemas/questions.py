from typing import List, Optional, Union, Any, Literal

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


class SwipeCard(BaseModel):
    content: str
    correct_swipe: Literal["left", "right"]
    explanation: str


class SwipeLabels(BaseModel):
    left: str
    right: str


class SwipeDecisionContent(BaseModel):
    cards: List[SwipeCard]
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
    id: str
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


# Union type for question content
QuestionContent = Union[
    FindErrorContent,
    StrikeOutContent,
    OrderingContent,
    HighlightContent,
    SwipeDecisionContent,
    MultipleChoiceContent,
    FillGapContent,
    MatchingContent,
    GraphPointContent,
    TrendArrowContent,
    SliderValueContent,
]


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


class GeneratedQuestion(BaseModel):
    type: QuestionType
    text: str
    content: dict[str, Any]


class ListNodeRelationsResponse(BaseModel):
    questions: List[GeneratedQuestion] = Field(
        ...,
        description="List of generated questions for the lesson node"
    )


class NodeDetailedRead(BaseModel):
    id: int
    passage_id: int
    title: str
    content: Optional[str]
    is_boss: bool
    config: dict
    pass_score: Optional[int]
    reward_coins: Optional[int]
    reward_xp: Optional[int]
    questions: List[QuestionRead] = []

    class Config:
        from_attributes = True


# --- Progress/Attempt schemas ---

class NodeProgressCreate(BaseModel):
    accuracy: float = Field(..., ge=0, le=1, description="Accuracy as decimal 0-1")
    correct_answer: int = Field(..., ge=0, description="Number of correct answers")
    total_questions: int = Field(..., ge=1, description="Total questions attempted")


class NodeProgressRead(BaseModel):
    id: int
    node_id: int
    accuracy: float
    correct_answer: int
    xp: float
    created_at: Any

    class Config:
        from_attributes = True


class UserAnswerInput(BaseModel):
    question_id: int
    user_answer: Any = Field(..., description="User's answer (varies by question type)")


class AIFeedbackRequest(BaseModel):
    answers: List[UserAnswerInput] = Field(..., min_length=1)


class WrongQuestionFeedback(BaseModel):
    question_id: int
    question_text: str
    user_answer: Any
    correct_answer: Any
    explanation: str


class AIFeedbackResponse(BaseModel):
    overall_feedback: str
    wrong_questions: List[WrongQuestionFeedback]
    accuracy: float
    retest_recommended: bool
    improvement_tips: List[str]


class QuestionReorder(BaseModel):
    question_id: int
    order_index: int
