from typing import Sequence

from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from src.models.passage_nodes import PassageNode
from src.models.passages import Passage
from src.models.user_node_progresses import UserNodeProgress
from src.models.user_villages import UserVillage
from src.repositories.base import BaseRepository


class PassageRepository(BaseRepository[Passage]):
    model = Passage

    async def get_by_village_id(self, village_id: int) -> Sequence[Passage]:
        stmt = (
            select(Passage)
            .where(Passage.village_id == village_id)
            .order_by(Passage.order_index)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_full(self, passage_id: int) -> Passage | None:
        stmt = (
            select(Passage)
            .options(
                joinedload(Passage.boss),
                joinedload(Passage.nodes),
            )
            .where(Passage.id == passage_id)
        )
        result = await self._session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def current_user_passage(self, user_id: int, subject: str) -> Passage | None:
        stmt_max_id = (
            select(func.max(Passage.id))
            .join(PassageNode, PassageNode.passage_id == Passage.id)
            .join(UserNodeProgress, UserNodeProgress.node_id == PassageNode.id)
            .join(UserVillage, UserVillage.village_id == Passage.village_id)
            .where(
                UserNodeProgress.user_id == user_id,
                UserVillage.subject == subject,
                UserVillage.user_id == user_id,
            )
        )

        max_id = (await self._session.execute(stmt_max_id)).scalar_one_or_none()
        if not max_id:
            return None

        stmt = select(Passage).where(Passage.id == max_id)
        passage = (await self._session.execute(stmt)).scalar_one_or_none()
        return passage
