from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.app.constants import BuildingType, SubjectEnum
from src.models.buildings import Building
from src.models.user_villages import UserVillage
from src.repositories.base import BaseRepository


class UserVillageRepository(BaseRepository[UserVillage]):
    model = UserVillage

    async def get_by_user_id(self, user_id: int) -> Sequence[UserVillage]:
        stmt = select(UserVillage).where(UserVillage.user_id == user_id)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_by_user_id_with_villages(self, user_id: int) -> Sequence[UserVillage]:
        stmt = (
            select(UserVillage)
            .where(UserVillage.user_id == user_id)
            .options(selectinload(UserVillage.village))
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_by_user_and_village(
            self,
            user_id: int,
            village_id: int
    ) -> UserVillage | None:
        stmt = select(UserVillage).where(
            UserVillage.user_id == user_id,
            UserVillage.village_id == village_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_and_village_subject(
            self,
            user_id: int,
            subject: SubjectEnum | str,
    ) -> UserVillage | None:
        stmt = select(UserVillage).where(
            UserVillage.user_id == user_id,
            UserVillage.subject == subject,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_and_subject_with_village(
            self,
            user_id: int,
            subject: SubjectEnum | str,
    ) -> UserVillage | None:
        stmt = (
            select(UserVillage)
            .where(
                UserVillage.user_id == user_id,
                UserVillage.subject == subject,
            )
            .options(selectinload(UserVillage.village))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_treasure(
            self, user_village_id: int, treasure_amount: int
    ) -> UserVillage | None:
        user_village = await self.get_by_id(user_village_id)
        if not user_village:
            return None
        user_village.treasure_amount = treasure_amount
        user_village.last_update_at = datetime.now(timezone.utc)
        await self._session.flush()
        return user_village

    async def collect_treasure(self, user_village_id: int) -> tuple[UserVillage | None, int]:
        user_village = await self.get_by_id(user_village_id)
        if not user_village:
            return None, 0

        collected = user_village.treasure_amount
        user_village.treasure_amount = 0
        user_village.last_collect_date = datetime.now(timezone.utc)
        await self._session.flush()
        return user_village, collected

    async def get_user_next_village(self, user_id: int, subject: SubjectEnum | str) -> Building | None:
        stmt = (
            select(UserVillage)
            .where(
                UserVillage.user_id == user_id,
                UserVillage.subject == subject
            )
            .options(selectinload(UserVillage.village))
        )
        result = await self._session.execute(stmt)
        user_village = result.scalar_one_or_none()

        if not user_village or not user_village.village:
            stmt = select(Building).where(
                Building.order_index == 1,
                Building.type == BuildingType.VILLAGE,
            )
            result = await self._session.execute(stmt)
            return result.scalar_one_or_none()

        stmt = select(Building).where(
            Building.order_index == user_village.village.order_index + 1,
            Building.type == BuildingType.VILLAGE,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def upgrade_village(self, user_village_id: int, new_village_id: int) -> UserVillage | None:
        user_village = await self.get_by_id(user_village_id)
        if not user_village:
            return None

        user_village.village_id = new_village_id
        user_village.treasure_amount = 0  # Reset treasure on upgrade
        await self._session.flush()
        return user_village
