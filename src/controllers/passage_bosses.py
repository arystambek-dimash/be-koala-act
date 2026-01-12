from src.app.errors import NotFoundException, BadRequestException
from src.app.uow import UoW
from src.models.passage_bosses import PassageBoss
from src.presentations.schemas.passages import PassageBossCreate, PassageBossUpdate
from src.repositories import PassageBossRepository, PassageRepository


class PassageBossController:
    def __init__(
            self,
            uow: UoW,
            passage_boss_repository: PassageBossRepository,
            passage_repository: PassageRepository,
    ):
        self._uow = uow
        self._passage_boss_repository = passage_boss_repository
        self._passage_repository = passage_repository

    async def create(self, data: PassageBossCreate) -> PassageBoss:
        passage = await self._passage_repository.get_by_id(data.passage_id)
        if not passage:
            raise NotFoundException(f"Passage with id {data.passage_id} not found")

        existing_boss = await self._passage_boss_repository.get_by_passage_id(data.passage_id)
        if existing_boss:
            raise BadRequestException(f"Boss already exists for passage {data.passage_id}")

        async with self._uow:
            boss = await self._passage_boss_repository.create(
                passage_id=data.passage_id,
                title=data.title,
                config=data.config,
                pass_score=data.pass_score,
                reward_coins=data.reward_coins,
                reward_xp=data.reward_xp,
            )
            return boss

    async def update(self, boss_id: int, data: PassageBossUpdate) -> PassageBoss:
        boss = await self._passage_boss_repository.get_by_id(boss_id)
        if not boss:
            raise NotFoundException(f"Boss with id {boss_id} not found")

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise BadRequestException("No fields to update")

        async with self._uow:
            updated = await self._passage_boss_repository.update(boss_id, **update_data)
            return updated

    async def delete(self, boss_id: int) -> bool:
        boss = await self._passage_boss_repository.get_by_id(boss_id)
        if not boss:
            raise NotFoundException(f"Boss with id {boss_id} not found")

        async with self._uow:
            return await self._passage_boss_repository.delete(boss_id)
