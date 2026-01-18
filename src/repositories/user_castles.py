from datetime import datetime, timezone, date
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.orm import aliased

from src.app.constants import BuildingType
from src.models.buildings import Building
from src.models.user_castles import UserCastle
from src.repositories.base import BaseRepository


class UserCastleRepository(BaseRepository[UserCastle]):
    model = UserCastle

    async def get_user_castle(self, user_id: int) -> dict[str, Any] | None:
        Next = aliased(Building)

        stmt = (
            select(
                UserCastle.id.label("user_castle_id"),
                UserCastle.user_id,
                UserCastle.treasure_amount,
                UserCastle.last_collect_date,
                UserCastle.taps_used_today,
                UserCastle.last_tap_reset_date,

                Building.id.label("castle_id"),
                Building.title.label("castle_title"),
                Building.svg.label("castle_svg"),
                Building.treasure_capacity,
                Building.speed_production_treasure,
                Building.cost,

                Building.next_building_id.label("next_castle_id"),
                Next.title.label("next_castle_title"),
            )
            .join(Building, Building.id == UserCastle.castle_id)
            .outerjoin(Next, Next.id == Building.next_building_id)
            .where(
                UserCastle.user_id == user_id,
                Building.type == BuildingType.CASTLE,
            )
            .limit(1)
        )

        result = await self._session.execute(stmt)
        row = result.mappings().one_or_none()
        return dict(row) if row else None

    async def update_treasure(self, user_castle_id: int, treasure_amount: int) -> UserCastle | None:
        user_castle = await self.get_by_id(user_castle_id)
        if not user_castle:
            return None

        user_castle.treasure_amount = treasure_amount
        await self._session.flush()
        return user_castle

    async def collect_treasure(self, user_castle_id: int) -> tuple[UserCastle | None, int]:
        user_castle = await self.get_by_id(user_castle_id)
        if not user_castle:
            return None, 0

        collected = user_castle.treasure_amount
        user_castle.treasure_amount = 0
        user_castle.last_collect_date = datetime.now(timezone.utc)
        await self._session.flush()
        return user_castle, collected

    async def record_taps(self, user_castle_id: int, count: int) -> UserCastle | None:
        user_castle = await self.get_by_id(user_castle_id)
        if not user_castle:
            return None

        today = date.today()
        if user_castle.last_tap_reset_date != today:
            user_castle.taps_used_today = 0
            user_castle.last_tap_reset_date = today

        user_castle.taps_used_today += count
        await self._session.flush()
        return user_castle

    async def get_taps_remaining(self, user_castle_id: int, max_taps: int) -> int:
        user_castle = await self.get_by_id(user_castle_id)
        if not user_castle:
            return 0

        today = date.today()
        if user_castle.last_tap_reset_date != today:
            return max_taps

        return max(0, max_taps - user_castle.taps_used_today)

    async def upgrade_castle(self, user_castle_id: int, new_castle_id: int) -> UserCastle | None:
        user_castle = await self.get_by_id(user_castle_id)
        if not user_castle:
            return None

        user_castle.castle_id = new_castle_id
        user_castle.treasure_amount = 0
        await self._session.flush()
        return user_castle

    async def migrate_users_to_castle(self, old_castle_id: int, new_castle_id: int):
        stmt = (
            update(UserCastle)
            .where(UserCastle.castle_id == old_castle_id)
            .values(castle_id=new_castle_id)
        )
        await self._session.execute(stmt)
