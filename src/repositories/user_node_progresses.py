from sqlalchemy import select

from src.models.user_node_progresses import UserNodeProgress
from src.repositories.base import BaseRepository


class UserNodeProgressRepository(BaseRepository[UserNodeProgress]):
    model = UserNodeProgress

    async def get_by_user_and_node(
            self,
            user_id: int,
            node_id: int
    ) -> UserNodeProgress | None:
        stmt = select(UserNodeProgress).where(
            UserNodeProgress.user_id == user_id,
            UserNodeProgress.node_id == node_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_progress_by_node_ids(
            self,
            user_id: int,
            node_ids: list[int]
    ) -> list[UserNodeProgress]:
        stmt = select(UserNodeProgress).where(
            UserNodeProgress.user_id == user_id,
            UserNodeProgress.node_id.in_(node_ids),
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
