from typing import List

from src.app.constants import SubjectEnum
from src.app.errors import BadRequestException
from src.app.passage_node_generator import PassageNodeGenerator
from src.app.uow import UoW
from src.presentations.schemas.onboards import PassageOnboard, SingleSubjectOnboard
from src.presentations.schemas.users import UserRead
from src.repositories import PassageNodeRepository, UserVillageRepository


class SubjectOnboardController:
    def __init__(
            self,
            uow: UoW,
            user_village_repository: UserVillageRepository,
            node_repository: PassageNodeRepository,
            node_generator: PassageNodeGenerator,
    ):
        self._uow = uow
        self._user_village_repository = user_village_repository
        self._node_repository = node_repository
        self._node_generator = node_generator

    async def execute(
            self,
            user: UserRead,
            data: SingleSubjectOnboard,
            force: bool = False,
    ):
        async with self._uow:
            await self._validate_can_generate(user.id, data.passages, force)
            await self._ensure_village_exists(user.id, data.subject)

            result = await self._node_generator.generate(data.passages, user.id)

            return result

    async def _validate_can_generate(
            self,
            user_id: int,
            passages: List[PassageOnboard],
            force: bool,
    ) -> None:
        if not force:
            await self._check_nodes_completed(user_id, passages)

        await self._check_no_duplicate_nodes(user_id, passages)

    async def _check_nodes_completed(
            self,
            user_id: int,
            passages: List[PassageOnboard]
    ) -> None:
        passage_ids = [p.passage_id for p in passages]
        existing_count = await self._node_repository.count_nodes_by_passage_ids(passage_ids)
        if existing_count == 0:
            return

        has_incomplete = await self._node_repository.has_incomplete_nodes(user_id, passage_ids)
        if has_incomplete:
            raise BadRequestException(
                "Cannot generate new nodes. "
                "Please complete existing nodes first. "
                "Use force=true to override."
            )

    async def _check_no_duplicate_nodes(
            self,
            user_id: int,
            passages: List[PassageOnboard],
    ) -> None:
        passage_ids = [p.passage_id for p in passages]
        existing = await self._node_repository.get_nodes_by_passage_ids(passage_ids)

        if existing:
            existing_ids = {node.passage_id for node in existing}
            raise BadRequestException(
                f"Nodes already exist for passages: {list(existing_ids)}. "
                "Cannot regenerate nodes for the same passages."
            )

    async def _ensure_village_exists(self, user_id: int, subject: SubjectEnum) -> None:
        existing = await self._user_village_repository.get_by_user_and_village_subject(
            user_id, subject
        )
        if existing:
            return

        db_village = await self._user_village_repository.get_user_next_village(
            user_id, subject
        )
        if not db_village:
            raise BadRequestException(f"No village available for subject: {subject}")

        await self._user_village_repository.create(
            user_id=user_id,
            subject=subject,
            village_id=db_village.id,
        )
