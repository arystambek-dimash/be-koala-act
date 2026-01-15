from typing import Sequence

from sqlalchemy import select

from src.models.questions import Question
from src.repositories.base import BaseRepository


class QuestionRepository(BaseRepository[Question]):
    model = Question

    async def get_by_node_id(self, node_id: int) -> Sequence[Question]:
        stmt = select(Question).where(Question.node_id == node_id)
        result = await self._session.execute(stmt)
        return result.scalars().all()
