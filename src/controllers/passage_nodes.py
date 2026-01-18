from src.app.errors import BadRequestException, NotFoundException
from src.app.uow import UoW
from src.models.nodes import PassageNode
from src.presentations.schemas.nodes import (
    BossNodeCreate,
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

    async def delete_node(self, node_id: int) -> bool:
        node = await self._node_repository.get_by_id(node_id)
        if not node:
            raise NotFoundException(f"Node with id {node_id} not found")

        async with self._uow:
            return await self._node_repository.delete(node_id)

    async def get_boss(self, passage_id: int) -> PassageNode | None:
        passage = await self._passage_repository.get_by_id(passage_id)
        if not passage:
            raise NotFoundException(f"Passage with id {passage_id} not found")
        return passage.boss

    async def create_boss(self, passage_id: int, data: BossNodeCreate) -> PassageNode:
        passage = await self._passage_repository.get_by_id(passage_id)
        if not passage:
            raise NotFoundException(f"Passage with id {passage_id} not found")

        if passage.boss:
            raise BadRequestException(f"Passage {passage_id} already has a boss node")

        async with self._uow:
            node = await self._node_repository.create(
                passage_id=passage_id,
                title=data.title,
                content=data.content,
                config=data.config or {},
                is_boss=True,
                user_id=None,
                pass_score=data.pass_score,
                reward_coins=data.reward_coins,
                reward_xp=data.reward_xp,
            )
            return node

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
