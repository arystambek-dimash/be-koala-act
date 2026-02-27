from sqlalchemy import select

from src.models.experiences import Experience
from src.repositories.base import BaseRepository


class ExperienceRepository(BaseRepository[Experience]):
    model = Experience

    async def get_by_user_id(self, user_id: int) -> Experience | None:
        stmt = select(Experience).where(Experience.user_id == user_id).limit(1)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def add_xp(self, user_id: int, xp_amount: int) -> Experience:
        if xp_amount <= 0:
            exp = await self.get_by_user_id(user_id)
            if exp:
                return exp
            # Create if not exists
            return await self.create(user_id=user_id, level=1, current_xp=0)

        stmt = (
            select(Experience)
            .where(Experience.user_id == user_id)
            .limit(1)
            .with_for_update()
        )
        experience = (await self._session.execute(stmt)).scalar_one_or_none()

        # Auto-create Experience if not exists
        if not experience:
            experience = Experience(user_id=user_id, level=1, current_xp=0)
            self._session.add(experience)
            await self._session.flush()

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
