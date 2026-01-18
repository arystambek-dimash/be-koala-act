import base64

from src.app.cloudflare_r2 import CloudflareR2Service
from src.app.constants import BuildingType, SubjectEnum
from src.app.errors import NotFoundException, BadRequestException
from src.app.uow import UoW
from src.presentations.schemas.buildings import (
    BuildingWithPassagesRead,
    BuildingCastleCreate,
    BuildingCastleRead,
    BuildingVillageRead,
    BuildingVillageCreate,
    BuildingUpdate,
    BuildingCastleUserRead,
    BuildingVillageUserRead,
)
from src.presentations.schemas.passages import PassageRead
from src.repositories import BuildingRepository, PassageRepository, UserVillageRepository, UserCastleRepository


class BuildingController:
    def __init__(
            self,
            uow: UoW,
            building_repository: BuildingRepository,
            passage_repository: PassageRepository,
            user_village_repository: UserVillageRepository,
            user_castle_repository: UserCastleRepository,
            cloudflare_r2: CloudflareR2Service,
    ):
        self.uow = uow
        self.building_repository = building_repository
        self.passage_repository = passage_repository
        self.cloudflare_r2 = cloudflare_r2
        self.user_village_repository = user_village_repository
        self.user_castle_repository = user_castle_repository

    async def create_building(
            self,
            body: BuildingCastleCreate | BuildingVillageCreate,
            building_type: BuildingType
    ) -> BuildingCastleRead | BuildingVillageRead:
        modified_data = body.model_dump()
        svg_url = None
        if body.svg:
            key = self.cloudflare_r2.build_key(body.title, "svg")
            svg_bytes = base64.b64decode(body.svg)
            svg_url = await self.cloudflare_r2.upload_bytes(
                key=key,
                body=svg_bytes,
                content_type="image/svg+xml",
            )
        modified_data['svg'] = svg_url
        if body.next_building_id:
            next_building = await self.building_repository.get_by_id(body.next_building_id)
            if not next_building:
                raise BadRequestException("Wrong next building id")

        list_buildings = await self.building_repository.list_buildings(
            building_type=building_type,
            subject=body.subject if hasattr(body, "subject") else None,
        )
        last_building = list_buildings[-1] if list_buildings else None
        async with self.uow:
            created = await self.building_repository.create(**modified_data)
            if last_building:
                await self.building_repository.update(
                    id=last_building.id,
                    next_building_id=created.id,
                )
        if building_type == BuildingType.CASTLE:
            return BuildingCastleRead.model_validate(created)
        else:
            return BuildingVillageRead.model_validate(created)

    async def get_village_with_passages(
            self,
            building_id: int
    ) -> BuildingWithPassagesRead:
        building = await self.building_repository.get_by_id(building_id)
        if not building:
            raise NotFoundException("Building with this id not found")
        passages = await self.passage_repository.village_passages(
            building.id
        )
        return BuildingWithPassagesRead(
            id=building.id,
            title=building.title,
            type=building.type,
            svg=building.svg,
            treasure_capacity=building.treasure_capacity,
            speed_production_treasure=building.speed_production_treasure,
            cost=building.cost,
            subject=building.subject,
            next_building_id=building.next_building_id,
            passages=[PassageRead.model_validate(passage) for passage in passages],
        )

    async def admin_list_buildings(
            self,
            building_type: BuildingType,
            subject: SubjectEnum | None = None,
    ) -> list[BuildingCastleRead] | list[BuildingVillageRead]:
        if subject and building_type != BuildingType.VILLAGE:
            raise BadRequestException("Type must be Village to retrieve buildings via subject")
        buildings = await self.building_repository.list_buildings(
            building_type=building_type,
            subject=subject
        )
        if building_type == BuildingType.CASTLE:
            return [BuildingCastleRead.model_validate(c) for c in buildings]
        else:
            return [BuildingVillageRead.model_validate(c) for c in buildings]

    async def list_buildings(
            self,
            building_type: BuildingType,
            user_id: int,
            subject: SubjectEnum | None = None,
    ) -> list[BuildingCastleUserRead] | list[BuildingVillageUserRead]:
        if subject and building_type != BuildingType.VILLAGE:
            raise BadRequestException("Type must be Village to retrieve buildings via subject")
        buildings = await self.building_repository.list_buildings(
            building_type=building_type,
            subject=subject,
            user_id=user_id
        )
        if building_type == BuildingType.CASTLE:
            return [BuildingCastleUserRead.model_validate(c) for c in buildings]
        else:
            return [BuildingVillageUserRead.model_validate(c) for c in buildings]

    async def update_building(
            self,
            building_id: int,
            body: BuildingUpdate,
            building_type: BuildingType
    ) -> BuildingCastleRead | BuildingVillageRead:
        db_building = await self.building_repository.get_by_id(building_id)
        if not db_building:
            raise NotFoundException("Building with this id not found")
        payload = body.model_dump(exclude_unset=True)
        if payload.get("svg") is not None:
            if db_building.svg:
                await self.cloudflare_r2.delete_file(key=db_building.svg.split("/")[-1])
            svg_url = None
            svg_bytes = base64.b64decode(body.svg)
            if body.svg:
                key = self.cloudflare_r2.build_key(body.title or db_building.title, "svg")
                svg_url = await self.cloudflare_r2.upload_bytes(
                    key=key,
                    body=svg_bytes,
                    content_type="image/svg+xml"
                )
            payload['svg'] = svg_url
        async with self.uow:
            updated = await self.building_repository.update(building_id, **payload)
        if building_type == BuildingType.CASTLE:
            return BuildingCastleRead.model_validate(updated)
        else:
            return BuildingVillageRead.model_validate(updated)

    async def delete_building(self, building_id: int) -> bool:
        db_building = await self.building_repository.get_by_id(building_id)
        if not db_building:
            raise NotFoundException("Building not found")
        list_buildings = await self.building_repository.list_buildings(
            building_type=db_building.type,
            subject=db_building.subject
        )

        if len(list_buildings) <= 1:
            raise BadRequestException(
                f"Cannot delete the last {db_building.subject} village. Users must have at least one."
            )
        current_index = -1
        for i, b in enumerate(list_buildings):
            if b.id == building_id:
                current_index = i
                break

        target_migration_id = db_building.next_building_id

        if not target_migration_id:
            if current_index > 0:
                target_migration_id = list_buildings[current_index - 1].id
            else:
                raise BadRequestException("Cannot migrate users: no target building found")
        if db_building.svg:
            await self.cloudflare_r2.delete_file(key=db_building.svg.split("/")[-1])
        async with self.uow:
            print(current_index)
            if db_building.type == BuildingType.VILLAGE:
                await self.user_village_repository.migrate_users_to_village(
                    old_village_id=building_id,
                    new_village_id=target_migration_id
                )
            elif db_building.type == BuildingType.CASTLE:
                await self.user_castle_repository.migrate_users_to_castle(
                    old_castle_id=building_id,
                    new_castle_id=target_migration_id
                )
            print(db_building.__dict__)
            print(db_building.next_building_id)
            if current_index == 0 and db_building.next_building_id is not None:
                print("Updating")
                await self.building_repository.update(
                    id=target_migration_id,
                    **{
                        "cost": None
                    }
                )

            if current_index > 0:
                previous_building = list_buildings[current_index - 1]
                await self.building_repository.update(
                    previous_building.id,
                    **{
                        "next_building_id": db_building.next_building_id
                    }
                )

            deleted = await self.building_repository.delete(building_id)

        return deleted
