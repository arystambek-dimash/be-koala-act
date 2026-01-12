from typing import Sequence

from src.app.cloudflare_r2 import CloudflareR2Service
from src.app.errors import NotFoundException
from src.app.uow import UoW
from src.presentations.schemas.castles import BuildingCreate, BuildingRead
from src.repositories import BuildingRepository


class BuildingController:
    def __init__(
            self,
            uow: UoW,
            building_repository: BuildingRepository,
            cloudflare_r2: CloudflareR2Service
    ):
        self.uow = uow
        self.building_repository = building_repository
        self.cloudflare_r2 = cloudflare_r2

    async def create_building(self, body: BuildingCreate) -> BuildingRead:
        modified_data = body.dict()
        svg_url = None
        if body.svg:
            key = self.cloudflare_r2.build_key(body.title, "svg")
            svg_url = await self.cloudflare_r2.upload_bytes(key=key, body=body.svg)
        modified_data['svg'] = svg_url
        async with self.uow:
            created = await self.building_repository.create(**modified_data)
        return BuildingRead.from_orm(created)

    async def get_building(self, building_id: int) -> BuildingRead:
        building = await self.building_repository.get_by_id(building_id)
        if not building:
            raise NotFoundException("Building with this id not found")
        return BuildingRead.from_orm(building)

    async def get_buildings(self) -> list[BuildingRead]:
        async with self.uow:
            buildings: Sequence = await self.building_repository.get_all(order_type="order_index", order_field="asc")
        return [BuildingRead.from_orm(c) for c in buildings]

    async def update_castle(self, building_id: int, body: BuildingCreate) -> BuildingRead:
        db_building = await self.get_building(building_id)
        if not db_building:
            raise NotFoundException("Castle with this id not found")
        payload = body.dict(exclude_unset=True)
        if payload.get("svg") is not None:
            if db_building.svg:
                await self.cloudflare_r2.delete_file(key=db_building.svg.split("/")[-1])
            svg_url = None
            if body.svg:
                key = self.cloudflare_r2.build_key(body.title, "svg")
                svg_url = await self.cloudflare_r2.upload_bytes(key=key, body=body.svg)
            payload['svg'] = svg_url
        async with self.uow:
            updated = await self.building_repository.update(building_id, **payload)
        return BuildingRead.from_orm(updated)

    async def delete_building(self, building_id: int) -> bool:
        async with self.uow:
            deleted = await self.building_repository.delete(building_id)
        return deleted
