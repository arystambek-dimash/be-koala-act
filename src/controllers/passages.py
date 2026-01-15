from typing import Sequence

from src.app.constants import SubjectEnum
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

    async def get_all(self) -> Sequence[Passage]:
        return await self._passage_repository.get_all(
            order_field="order_index",
            order_type="asc",
        )

    async def get_by_id(self, passage_id: int) -> Passage:
        passage = await self._passage_repository.get_by_id_with_nodes(passage_id)
        if not passage:
            raise NotFoundException(f"Passage with id {passage_id} not found")
        return passage

    async def get_by_subject(self, subject: SubjectEnum) -> Sequence[Passage]:
        return await self._passage_repository.get_by_subject(subject)

    async def create(self, data: PassageCreate) -> Passage:
        village = await self._building_repository.get_by_id(data.village_id)
        if not village:
            raise NotFoundException(f"Village with id {data.village_id} not found")

        async with self._uow:
            passage = await self._passage_repository.create(
                village_id=data.village_id,
                subject=data.subject,
                title=data.title,
                order_index=data.order_index,
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
