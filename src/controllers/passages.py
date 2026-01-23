from typing import Sequence

from src.app.errors import BadRequestException, NotFoundException
from src.app.uow import UoW
from src.models.passages import Passage
from src.presentations.schemas.passages import (
    PassageCreate,
    PassageUpdate,
)
from src.repositories import PassageRepository, BuildingRepository


class PassageController:
    def __init__(
            self,
            uow: UoW,
            passage_repository: PassageRepository,
            building_repository: BuildingRepository,
    ):
        self._uow = uow
        self._passage_repository = passage_repository
        self._building_repository = building_repository

    async def create(self, data: PassageCreate) -> Passage:
        village = await self._building_repository.get_by_id(data.village_id)
        if not village:
            raise NotFoundException(f"Village with id {data.village_id} not found")

        # Get next order_index for this village
        passages = await self._passage_repository.village_passages(data.village_id)
        next_order = len(passages) + 1

        async with self._uow:
            passage = await self._passage_repository.create(
                village_id=data.village_id,
                title=data.title,
                order_index=next_order
            )
            return passage

    async def update(self, passage_id: int, data: PassageUpdate) -> Passage:
        passage = await self._passage_repository.get_by_id(passage_id)
        if not passage:
            raise NotFoundException(f"Passage with id {passage_id} not found")

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise BadRequestException("No fields to update")

        async with self._uow:
            updated = await self._passage_repository.update(passage_id, **update_data)
            return updated

    async def delete(self, passage_id: int) -> bool:
        passage = await self._passage_repository.get_by_id(passage_id)
        if not passage:
            raise NotFoundException(f"Passage with id {passage_id} not found")

        async with self._uow:
            return await self._passage_repository.delete(passage_id)

    async def reorder_passage(
            self,
            village_id: int,
            passage_id: int,
            new_index: int
    ) -> Sequence[Passage]:
        passage = await self._passage_repository.get_by_id(passage_id)
        if not passage:
            raise NotFoundException(f"Passage with id {passage_id} not found")
        if passage.village_id != village_id:
            raise BadRequestException(f"Passage {passage_id} does not belong to village {village_id}")

        async with self._uow:
            await self._passage_repository.reorder(
                item_id=passage_id,
                new_index=new_index,
                fk_name="village_id",
                fk_id=village_id,
            )
        return await self._passage_repository.village_passages(village_id)

    async def get_next_passages(
            self,
            user_id: int,
            village_id: int,
            limit: int = 5,
    ):
        village = await self._building_repository.get_by_id(village_id)
        if not village:
            raise NotFoundException(f"Village with id {village_id} not found")

        passages = await self._passage_repository.get_next_passages(user_id, village_id, limit)
        return passages
