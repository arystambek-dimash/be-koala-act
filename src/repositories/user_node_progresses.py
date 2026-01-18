from typing import Sequence

from sqlalchemy import select

from src.models.node_progresses import UserNodeProgress
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

    async def get_all_attempts(
            self,
            user_id: int,
            node_id: int,
    ) -> Sequence[UserNodeProgress]:
        """Get all attempts/progress records for a user on a specific node."""
        stmt = (
            select(UserNodeProgress)
            .where(
                UserNodeProgress.user_id == user_id,
                UserNodeProgress.node_id == node_id,
            )
            .order_by(UserNodeProgress.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def create_progress(
            self,
            user_id: int,
            node_id: int,
            accuracy: float,
            correct_answer: int,
            xp: float,
    ) -> UserNodeProgress:
        """Create a new progress record."""
        progress = UserNodeProgress(
            user_id=user_id,
            node_id=node_id,
            accuracy=accuracy,
            correct_answer=correct_answer,
            xp=xp,
        )
        self._session.add(progress)
        await self._session.flush()
        await self._session.refresh(progress)
        return progress
