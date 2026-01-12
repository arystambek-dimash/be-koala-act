from sqlalchemy import select

from src.models.passage_bosses import PassageBoss
from src.repositories.base import BaseRepository


class PassageBossRepository(BaseRepository[PassageBoss]):
    model = PassageBoss

    async def get_by_passage_id(self, passage_id: int) -> PassageBoss | None:
        stmt = select(PassageBoss).where(PassageBoss.passage_id == passage_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
