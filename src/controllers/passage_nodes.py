from typing import Sequence

from src.app.errors import BadRequestException, NotFoundException
from src.app.uow import UoW
from src.models.passage_nodes import PassageNode
from src.presentations.schemas.nodes import (
    PassageNodeCreate,
    PassageNodeUpdate,
    BossNodeUpdate,
)
from src.repositories import PassageNodeRepository, PassageRepository


class PassageNodeController:
    def __init__(
            self,
            uow: UoW,
            node_repository: PassageNodeRepository,
            passage_repository: PassageRepository,
    ):
        self._uow = uow
        self._node_repository = node_repository
        self._passage_repository = passage_repository

    async def get_nodes_by_passage(self, passage_id: int) -> Sequence[PassageNode]:
        passage = await self._passage_repository.get_by_id(passage_id)
        if not passage:
            raise NotFoundException(f"Passage with id {passage_id} not found")
        return await self._node_repository.get_nodes_by_passage_ids([passage_id])

    async def get_node(self, node_id: int) -> PassageNode:
        node = await self._node_repository.get_by_id_with_passage(node_id)
        if not node:
            raise NotFoundException(f"Node with id {node_id} not found")
        return node

    async def create_node(self, passage_id: int, data: PassageNodeCreate) -> PassageNode:
        passage = await self._passage_repository.get_by_id(passage_id)
        if not passage:
            raise NotFoundException(f"Passage with id {passage_id} not found")

        max_order = await self._node_repository.get_max_order_index(passage_id)

        async with self._uow:
            node = await self._node_repository.create(
                passage_id=passage_id,
                title=data.title,
                content=data.content,
                order_index=data.order_index or (max_order + 1),
                is_boss=True,
            )
            return node

    async def update_node(self, node_id: int, data: PassageNodeUpdate) -> PassageNode:
        node = await self._node_repository.get_by_id(node_id)
        if not node:
            raise NotFoundException(f"Node with id {node_id} not found")

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise BadRequestException("No fields to update")

        async with self._uow:
            updated = await self._node_repository.update(node_id, **update_data)
            return updated

    async def delete_node(self, node_id: int) -> bool:
        node = await self._node_repository.get_by_id(node_id)
        if not node:
            raise NotFoundException(f"Node with id {node_id} not found")

        async with self._uow:
            return await self._node_repository.delete(node_id)

    async def update_boss(self, node_id: int, data: BossNodeUpdate) -> PassageNode:
        node = await self._node_repository.get_by_id(node_id)
        if not node:
            raise NotFoundException(f"Node with id {node_id} not found")

        if not node.is_boss:
            raise BadRequestException(f"Node {node_id} is not a boss node")

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise BadRequestException("No fields to update")

        async with self._uow:
            updated = await self._node_repository.update(node_id, **update_data)
            return updated
