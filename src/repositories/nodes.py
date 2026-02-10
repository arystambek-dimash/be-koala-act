from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.models.nodes import PassageNode
from src.repositories.base import BaseRepository


class PassageNodeRepository(BaseRepository[PassageNode]):
    model = PassageNode

    async def get_by_id(self, id: int) -> PassageNode | None:
        stmt = select(PassageNode).where(
            PassageNode.id == id
        ).options(
            selectinload(PassageNode.questions)
        )
        return (await self._session.execute(stmt)).scalar_one_or_none()
