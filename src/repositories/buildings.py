from typing import Optional

from sqlalchemy import select

from src.app.constants import BuildingType
from src.models.buildings import Building
from src.models.user_castles import UserCastle
from src.models.user_villages import UserVillage
from src.repositories.base import BaseRepository


class BuildingRepository(BaseRepository[Building]):
    model = Building

    async def get_user_next_building(
            self,
            user_id: int,
            building_type: BuildingType,
            current_user_building_id: int | None = None,
            subject: Optional[str] = None,
    ) -> Building | None:
        if building_type == BuildingType.VILLAGE and not subject:
            raise ValueError("subject is required for VILLAGE")

        UserBuilding = UserCastle if building_type == BuildingType.CASTLE else UserVillage
        building_fk = UserBuilding.castle_id if building_type == BuildingType.CASTLE else UserBuilding.village_id
        if current_user_building_id is None:
            stmt = (
                select(Building)
                .where(Building.type == building_type)
                .order_by(Building.order_index.asc())
                .limit(1)
            )
            result = await self._session.execute(stmt)
            return result.scalar_one_or_none()

        current_order_subq = (
            select(Building.order_index)
            .select_from(UserBuilding)
            .join(Building, Building.id == building_fk)
            .where(
                UserBuilding.user_id == user_id,
                UserBuilding.id == current_user_building_id,
                Building.type == building_type,
            )
        )

        if building_type == BuildingType.VILLAGE:
            current_order_subq = current_order_subq.where(UserBuilding.subject == subject)

        current_order_subq = current_order_subq.scalar_subquery()
        stmt = (
            select(Building)
            .where(
                Building.type == building_type,
                Building.order_index > current_order_subq,
            )
            .order_by(Building.order_index.asc())
            .limit(1)
        )

        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
