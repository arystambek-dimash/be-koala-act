from typing import Sequence

from sqlalchemy import select, func, exists
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import selectinload

from src.models.passage_nodes import PassageNode
from src.models.user_node_progresses import UserNodeProgress
from src.repositories.base import BaseRepository


class PassageNodeRepository(BaseRepository[PassageNode]):
    model = PassageNode

    async def get_by_id_with_passage(self, node_id: int) -> PassageNode | None:
        stmt = (
            select(PassageNode)
            .where(PassageNode.id == node_id)
            .options(
                selectinload(PassageNode.passage),
                selectinload(PassageNode.questions),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_nodes_by_passage_ids(
            self, passage_ids: list[int]
    ) -> Sequence[PassageNode]:
        stmt = (
            select(PassageNode)
            .where(PassageNode.passage_id.in_(passage_ids), PassageNode.is_boss == True)
            .order_by(PassageNode.order_index)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def has_incomplete_nodes(self, user_id: int, passage_ids: list[int]) -> bool:
        subquery = (
            select(UserNodeProgress.node_id)
            .where(UserNodeProgress.user_id == user_id)
        )
        stmt = (
            select(exists().where(
                PassageNode.passage_id.in_(passage_ids),
                ~PassageNode.id.in_(subquery)
            ))
        )
        result = await self._session.execute(stmt)
        return result.scalar()

    async def count_nodes_by_passage_ids(self, passage_ids: list[int]) -> int:
        stmt = (
            select(func.count(PassageNode.id))
            .where(PassageNode.passage_id.in_(passage_ids))
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def get_max_order_index(self, passage_id: int) -> int:
        stmt = (
            select(func.coalesce(func.max(PassageNode.order_index), 0))
            .where(PassageNode.passage_id == passage_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def bulk_create(self, nodes: list[dict]) -> Sequence[PassageNode]:
        if not nodes:
            return []
        stmt = insert(PassageNode).values(nodes).returning(PassageNode)
        result = await self._session.execute(stmt)
        return result.scalars().all()
