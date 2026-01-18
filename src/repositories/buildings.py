from typing import Mapping, Any, Sequence

from sqlalchemy import select

from src.app.constants import SubjectEnum, BuildingType
from src.models.buildings import Building
from src.models.user_castles import UserCastle
from src.models.user_villages import UserVillage
from src.repositories.base import BaseRepository
from src.repositories.utils_repositories import UtilsRepository


class BuildingRepository(BaseRepository[Building], UtilsRepository):
    model = Building

    async def list_buildings(
            self,
            *,
            building_type: BuildingType,
            user_id: int | None = None,
            subject: SubjectEnum | None = None,
    ) -> Sequence[Building]:
        stmt = (
            select(
                Building
            )
            .where(Building.type == building_type)
            .order_by(Building.id.asc())
        )

        if building_type == BuildingType.VILLAGE:
            if subject is None:
                stmt = stmt.where(Building.subject.isnot(None))
            else:
                stmt = stmt.where(Building.subject == subject)
        if user_id is not None:
            if building_type == BuildingType.CASTLE:
                stmt = stmt.add_columns(
                    (UserCastle.castle_id == Building.id).label("is_current")
                ).outerjoin(
                    UserCastle,
                    UserCastle.user_id == user_id,
                )
            else:
                stmt = stmt.add_columns(
                    (UserVillage.village_id == Building.id).label("is_current")
                ).outerjoin(
                    UserVillage,
                    (
                            UserVillage.user_id == user_id
                    )
                    &
                    (
                            UserVillage.village_id == Building.id
                    )
                )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_user_next_castle(self, user_id: int) -> Building | None:
        user_castle_id = await self._session.scalar(
            select(UserCastle.castle_id).where(UserCastle.user_id == user_id)
        )

        if user_castle_id is None:
            return await self._session.scalar(
                select(Building)
                .where(Building.type == BuildingType.CASTLE)
                .order_by(Building.id.asc())
                .limit(1)
            )

        next_id = await self._session.scalar(
            select(Building.next_building_id).where(Building.id == user_castle_id)
        )
        if next_id is None:
            return None

        return await self._session.scalar(
            select(Building).where(
                Building.id == next_id,
                Building.type == BuildingType.CASTLE,
            )
        )

    async def get_user_next_village(self, user_id: int, subject: SubjectEnum) -> Building | None:
        current_village_id = await self._session.scalar(
            select(UserVillage.village_id)
            .join(Building, Building.id == UserVillage.village_id)
            .where(
                UserVillage.user_id == user_id,
                Building.type == BuildingType.VILLAGE,
                Building.subject == subject,
            )
        )

        if current_village_id is None:
            return await self._session.scalar(
                select(Building)
                .where(
                    Building.type == BuildingType.VILLAGE,
                    Building.subject == subject,
                )
                .order_by(Building.id.asc())
                .limit(1)
            )

        next_id = await self._session.scalar(
            select(Building.next_building_id).where(Building.id == current_village_id)
        )
        if next_id is None:
            return None

        return await self._session.scalar(
            select(Building).where(
                Building.id == next_id,
                Building.type == BuildingType.VILLAGE,
                Building.subject == subject,
            )
        )
