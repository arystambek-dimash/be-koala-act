from typing import Sequence

from sqlalchemy import select, asc

from src.models.questions import Question
from src.repositories.base import BaseRepository
from src.repositories.utils_repositories import UtilsRepository


class QuestionRepository(BaseRepository[Question], UtilsRepository):
    model = Question

    async def get_by_node_id(self, node_id: int) -> Sequence[Question]:
        stmt = select(Question).where(Question.node_id == node_id).order_by(asc(Question.order_index))
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def count_by_node_id(self, node_id: int) -> int:
        from sqlalchemy import func
        stmt = select(func.count()).select_from(Question).where(Question.node_id == node_id)
        result = await self._session.execute(stmt)
        return result.scalar() or 0
