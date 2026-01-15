from typing import Sequence

from src.app.errors import BadRequestException, NotFoundException
from src.app.uow import UoW
from src.models.questions import Question
from src.presentations.schemas.questions import (
    QuestionCreate,
    QuestionUpdate,
)
from src.repositories import QuestionRepository, PassageNodeRepository


class QuestionController:
    def __init__(
            self,
            uow: UoW,
            question_repository: QuestionRepository,
            node_repository: PassageNodeRepository,
    ):
        self._uow = uow
        self._question_repository = question_repository
        self._node_repository = node_repository

    async def get_by_node_id(self, node_id: int) -> Sequence[Question]:
        node = await self._node_repository.get_by_id(node_id)
        if not node:
            raise NotFoundException(f"Node with id {node_id} not found")
        return await self._question_repository.get_by_node_id(node_id)

    async def create(self, node_id: int, data: QuestionCreate) -> Question:
        node = await self._node_repository.get_by_id(node_id)
        if not node:
            raise NotFoundException(f"Node with id {node_id} not found")

        async with self._uow:
            question = await self._question_repository.create(
                node_id=node_id,
                type=data.type.value,
                content=data.content,
            )
            return question

    async def update(self, question_id: int, data: QuestionUpdate) -> Question:
        question = await self._question_repository.get_by_id(question_id)
        if not question:
            raise NotFoundException(f"Question with id {question_id} not found")

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise BadRequestException("No fields to update")

        if "type" in update_data and update_data["type"]:
            update_data["type"] = update_data["type"].value

        async with self._uow:
            updated = await self._question_repository.update(question_id, **update_data)
            return updated

    async def delete(self, question_id: int) -> bool:
        question = await self._question_repository.get_by_id(question_id)
        if not question:
            raise NotFoundException(f"Question with id {question_id} not found")

        async with self._uow:
            return await self._question_repository.delete(question_id)
