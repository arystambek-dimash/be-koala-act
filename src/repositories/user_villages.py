from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select, update, and_
from sqlalchemy.orm import aliased

from src.app.constants import BuildingType
from src.models.buildings import Building
from src.models.user_villages import UserVillage
from src.repositories.base import BaseRepository


class UserVillageRepository(BaseRepository[UserVillage]):
    model = UserVillage

    async def get_user_villages(self, user_id: int) -> list[dict[str, Any]]:
        Next = aliased(Building)

        stmt = (
            select(
                UserVillage.id.label("user_village_id"),
                UserVillage.user_id,
                UserVillage.treasure_amount,
                UserVillage.last_collect_date,
                UserVillage.last_update_at,

                Building.id.label("village_id"),
                Building.title.label("village_title"),
                Building.svg.label("village_svg"),
                Building.subject.label("village_subject"),

                Building.next_building_id.label("next_building_id"),
                Next.title.label("next_building_title"),

                Building.treasure_capacity,
                Building.speed_production_treasure,
                Building.cost,
            )
            .join(Building, Building.id == UserVillage.village_id)
            .outerjoin(Next, Next.id == Building.next_building_id)
            .where(
                UserVillage.user_id == user_id,
                Building.type == BuildingType.VILLAGE,
            )
            .order_by(Building.subject.asc(), Building.id.asc())
        )

        result = await self._session.execute(stmt)
        return [dict(r) for r in result.mappings().all()]

    async def get_village_by_user(
            self,
            user_id: int,
            village_id: int,
    ) -> dict[str, Any] | None:
        stmt = (
            select(
                UserVillage.id.label("user_village_id"),
                UserVillage.user_id,
                UserVillage.treasure_amount,
                UserVillage.last_collect_date,
                UserVillage.last_update_at,
                Building.id.label("village_id"),
                Building.title.label("village_title"),
                Building.svg.label("village_svg"),
                Building.subject.label("village_subject"),
                Building.treasure_capacity,
                Building.speed_production_treasure,
                Building.cost,
                Building.next_building_id,
            )
            .join(Building, Building.id == UserVillage.village_id)
            .where(
                UserVillage.user_id == user_id,
                UserVillage.village_id == village_id
            )
        )
        result = await self._session.execute(stmt)
        row = result.mappings().one_or_none()
        return dict(row) if row else None

    async def get_village_by_user_subject(
            self,
            user_id: int,
            subject: str,
    ) -> dict[str, Any] | None:
        stmt = (
            select(
                UserVillage.id.label("user_village_id"),
                UserVillage.user_id,
                UserVillage.treasure_amount,
                UserVillage.last_collect_date,
                UserVillage.last_update_at,
                Building.id.label("village_id"),
                Building.title.label("village_title"),
                Building.svg.label("village_svg"),
                Building.subject.label("village_subject"),
                Building.treasure_capacity,
                Building.speed_production_treasure,
                Building.cost,
                Building.next_building_id,
            )
            .join(
                Building,
                and_(
                    Building.id == UserVillage.village_id,
                    Building.subject == subject
                )
            )
            .where(UserVillage.user_id == user_id)
        )
        result = await self._session.execute(stmt)
        row = result.mappings().one_or_none()
        return dict(row) if row else None

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

    async def upgrade_village(self, user_village_id: int, new_village_id: int) -> UserVillage | None:
        user_village = await self.get_by_id(user_village_id)
        if not user_village:
            return None

        user_village.village_id = new_village_id
        user_village.treasure_amount = 0
        await self._session.flush()
        return user_village

    async def migrate_users_to_village(self, old_village_id: int, new_village_id: int):
        stmt = (
            update(UserVillage)
            .where(UserVillage.village_id == old_village_id)
            .values(village_id=new_village_id)
        )
        await self._session.execute(stmt)
