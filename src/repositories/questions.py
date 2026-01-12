from src.models.questions import Question
from src.repositories.base import BaseRepository


class QuestionRepository(BaseRepository[Question]):
    model = Question
