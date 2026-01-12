from sqlalchemy import select

from src.models.experiences import Experience
from src.repositories.base import BaseRepository


class ExperienceRepository(BaseRepository[Experience]):
    model = Experience

    async def get_by_user_id(self, user_id: int) -> Experience | None:
        stmt = select(Experience).where(Experience.user_id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def add_xp(self, user_id: int, xp_amount: int) -> Experience:
        if xp_amount <= 0:
            return await self.get_by_user_id(user_id)

        stmt = (
            select(Experience)
            .where(Experience.user_id == user_id)
            .with_for_update()
        )
        experience = (await self._session.execute(stmt)).scalar_one()

        from src.app.constants import MAX_LEVEL

        experience.current_xp += xp_amount

        while experience.level < MAX_LEVEL and experience.current_xp >= experience.capacity:
            experience.current_xp -= experience.capacity
            experience.level += 1

        if experience.level >= MAX_LEVEL:
            experience.level = MAX_LEVEL
            experience.current_xp = min(experience.current_xp, experience.capacity - 1)

        await self._session.flush()
        return experience
