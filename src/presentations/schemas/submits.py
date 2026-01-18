from typing import List, Literal, Union, Annotated

from pydantic import BaseModel, Field


class MultipleChoiceOptions(BaseModel):
    id: str


class MultipleChoiceSubmit(BaseModel):
    options: List[MultipleChoiceOptions]


class FindErrorContentSubmit(BaseModel):
    error_index: int


class StrikeOutSubmit(BaseModel):
    removed_ids: List[int]


class OrderingSubmit(BaseModel):
    ordered_items: List[str]


class HighlightSubmit(BaseModel):
    selected_phrase: str


class SwipeDecisionSubmit(BaseModel):
    swipe: Literal["left", "right"]


class FillGapSubmit(BaseModel):
    answer: str


class MatchingPairSubmit(BaseModel):
    left: str
    right: str


class MatchingSubmit(BaseModel):
    matches: List[MatchingPairSubmit]


class GraphPointSubmit(BaseModel):
    x: float
    y: float


class TrendArrowSubmit(BaseModel):
    trend: Literal["increase", "decrease", "no_change"]


class SliderValueSubmit(BaseModel):
    value: float


# --- Discriminated question submits ---
class MultipleChoiceQuestionSubmit(BaseModel):
    question_id: int
    question_type: Literal["multiple_choice"]
    content: MultipleChoiceSubmit


class FindErrorQuestionSubmit(BaseModel):
    question_id: int
    question_type: Literal["find_error"]
    content: FindErrorContentSubmit


class StrikeOutQuestionSubmit(BaseModel):
    question_id: int
    question_type: Literal["strike_out"]
    content: StrikeOutSubmit


class OrderingQuestionSubmit(BaseModel):
    question_id: int
    question_type: Literal["ordering"]
    content: OrderingSubmit


class HighlightQuestionSubmit(BaseModel):
    question_id: int
    question_type: Literal["highlight"]
    content: HighlightSubmit


class SwipeDecisionQuestionSubmit(BaseModel):
    question_id: int
    question_type: Literal["swipe_decision"]
    content: SwipeDecisionSubmit


class FillGapQuestionSubmit(BaseModel):
    question_id: int
    question_type: Literal["fill_gap"]
    content: FillGapSubmit


class MatchingQuestionSubmit(BaseModel):
    question_id: int
    question_type: Literal["matching"]
    content: MatchingSubmit


class GraphPointQuestionSubmit(BaseModel):
    question_id: int
    question_type: Literal["graph_point"]
    content: GraphPointSubmit


class TrendArrowQuestionSubmit(BaseModel):
    question_id: int
    question_type: Literal["trend_arrow"]
    content: TrendArrowSubmit


class SliderValueQuestionSubmit(BaseModel):
    question_id: int
    question_type: Literal["slider_value"]
    content: SliderValueSubmit


SubmitContentType = Union[
    MultipleChoiceQuestionSubmit,
    FindErrorQuestionSubmit,
    StrikeOutQuestionSubmit,
    OrderingQuestionSubmit,
    HighlightQuestionSubmit,
    SwipeDecisionQuestionSubmit,
    FillGapQuestionSubmit,
    MatchingQuestionSubmit,
    GraphPointQuestionSubmit,
    TrendArrowQuestionSubmit,
    SliderValueQuestionSubmit,
]

QuestionSubmit = Annotated[
    SubmitContentType,
    Field(discriminator="question_type"),
]


class SubmitModel(BaseModel):
    node_id: int
    questions: List[QuestionSubmit]

class SubmitResponse(BaseModel):
    earned_xp: int
    accuracy: float
    correct_answers: int
