from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import selectinload, with_loader_criteria

from src.app.constants import SubjectEnum
from src.models.passage_nodes import PassageNode
from src.models.passages import Passage
from src.models.user_node_progresses import UserNodeProgress
from src.models.user_villages import UserVillage
from src.repositories.base import BaseRepository


class PassageRepository(BaseRepository[Passage]):
    model = Passage

    async def village_and_subject_passages(
            self,
            village_id: int,
            subject: str,
    ) -> Sequence[Passage]:
        stmt = (
            select(Passage)
            .where(
                Passage.village_id == village_id,
                Passage.subject == subject,
            )
            .order_by(Passage.order_index.asc())
        )
        return (await self._session.execute(stmt)).scalars().all()

    async def get_by_subject(self, subject: SubjectEnum) -> Sequence[Passage]:
        stmt = (
            select(Passage)
            .where(Passage.subject == subject)
            .order_by(Passage.order_index.asc())
            .options(
                selectinload(Passage.nodes),
                selectinload(Passage.boss),
            )
        )
        return (await self._session.execute(stmt)).scalars().all()

    async def get_by_id_with_nodes(self, passage_id: int) -> Passage | None:
        stmt = (
            select(Passage)
            .where(Passage.id == passage_id)
            .options(
                selectinload(Passage.nodes),
                selectinload(Passage.boss),
            )
        )
        return (await self._session.execute(stmt)).scalar_one_or_none()

    async def user_current_passage(
            self,
            user_id: int,
            village_id: int
    ) -> Passage | None:
        stmt = (
            select(Passage)
            .join(PassageNode, PassageNode.passage_id == Passage.id)
            .join(UserNodeProgress, UserNodeProgress.node_id == PassageNode.id)
            .join(UserVillage, UserVillage.village_id == Passage.village_id)
            .where(
                UserNodeProgress.user_id == user_id,
                UserVillage.user_id == user_id,
                UserVillage.village_id == village_id,
            )
            .order_by(Passage.order_index.desc(), Passage.id.desc())
            .limit(1)
        )
        return (await self._session.execute(stmt)).scalar_one_or_none()

    async def get_user_roadmap(
            self,
            user_id: int,
            village_id: int,
            passage_id: int | None,
            limit: int,
    ) -> Sequence[Passage]:

        if passage_id:
            current_order = (
                select(Passage.order_index)
                .where(Passage.id == passage_id)
                .scalar_subquery()
            )
            order_filter = Passage.order_index > current_order
        else:
            order_filter = Passage.order_index >= 0  # или > -1

        stmt = (
            select(Passage)
            .where(Passage.village_id == village_id, order_filter)
            .order_by(Passage.order_index.asc(), Passage.id.asc())
            .limit(limit)
            .options(
                selectinload(Passage.boss),
                selectinload(Passage.nodes),

                with_loader_criteria(
                    UserNodeProgress,
                    UserNodeProgress.user_id == user_id,
                    include_aliases=True,
                ),
                selectinload(Passage.nodes).selectinload(PassageNode.progresses),
            )
        )

        return (await self._session.execute(stmt)).scalars().all()
