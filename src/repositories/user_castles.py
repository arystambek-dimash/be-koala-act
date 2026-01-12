from datetime import datetime, timezone, date

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.app.constants import BuildingType
from src.models.buildings import Building
from src.models.user_castles import UserCastle
from src.repositories.base import BaseRepository


class UserCastleRepository(BaseRepository[UserCastle]):
    model = UserCastle

    async def get_by_user_id(self, user_id: int) -> UserCastle | None:
        stmt = select(UserCastle).where(UserCastle.user_id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_id_with_castle(self, user_id: int) -> UserCastle | None:
        stmt = (
            select(UserCastle)
            .where(UserCastle.user_id == user_id)
            .options(selectinload(UserCastle.castle))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

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

    async def record_tap(self, user_castle_id: int) -> UserCastle | None:
        user_castle = await self.get_by_id(user_castle_id)
        if not user_castle:
            return None

        today = date.today()
        if user_castle.last_tap_reset_date != today:
            user_castle.taps_used_today = 0
            user_castle.last_tap_reset_date = today

        user_castle.taps_used_today += 1
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

    async def get_user_next_castle(self, user_id: int) -> Building | None:
        stmt = (
            select(UserCastle)
            .where(UserCastle.user_id == user_id)
            .options(selectinload(UserCastle.castle))
        )
        result = await self._session.execute(stmt)
        user_castle = result.scalar_one_or_none()

        if not user_castle or not user_castle.castle:
            stmt = select(Building).where(
                Building.order_index == 1,
                Building.type == BuildingType.CASTLE,
            )
            result = await self._session.execute(stmt)
            return result.scalar_one_or_none()

        stmt = select(Building).where(
            Building.order_index == user_castle.castle.order_index + 1,
            Building.type == BuildingType.CASTLE,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def upgrade_castle(self, user_castle_id: int, new_castle_id: int) -> UserCastle | None:
        user_castle = await self.get_by_id(user_castle_id)
        if not user_castle:
            return None

        user_castle.castle_id = new_castle_id
        user_castle.treasure_amount = 0
        await self._session.flush()
        return user_castle
