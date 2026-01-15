from src.app.constants import SubjectEnum, BuildingType
from src.app.errors import BadRequestException
from src.app.passage_node_generator import PassageNodeGenerator
from src.app.uow import UoW
from src.presentations.schemas.onboards import SingleSubjectOnboard
from src.presentations.schemas.users import UserRead
from src.repositories import (
    PassageNodeRepository,
    UserVillageRepository,
    BuildingRepository
)


class SubjectOnboardController:
    def __init__(
            self,
            uow: UoW,
            user_village_repository: UserVillageRepository,
            node_repository: PassageNodeRepository,
            node_generator: PassageNodeGenerator,
            building_repository: BuildingRepository,
    ):
        self._uow = uow
        self._user_village_repository = user_village_repository
        self._node_repository = node_repository
        self._node_generator = node_generator
        self._building_repository = building_repository

    async def execute(
            self,
            user: UserRead,
            data: SingleSubjectOnboard,
    ):
        async with self._uow:
            passage_ids = [p.passage_id for p in data.passages]
            existing_count = await self._node_repository.count_nodes_by_passage_ids(passage_ids)
            if existing_count == 0:
                return
            has_incomplete = await self._node_repository.has_incomplete_nodes(user.id, passage_ids)
            if has_incomplete:
                raise BadRequestException(
                    "Cannot generate new nodes. "
                    "Please complete existing nodes first. "
                    "Use force=true to override."
                )

            await self._ensure_village_exists(user.id, data.subject)

            result = await self._node_generator.generate(data.passages)

            return result

    async def _ensure_village_exists(self, user_id: int, subject: SubjectEnum) -> None:
        existing = await (
            self._user_village_repository
            .village_by_user_and_subject(
                user_id, subject
            )
        )
        if existing:
            return
        db_village = await self._building_repository.get_user_next_building(
            user_id,
            building_type=BuildingType.VILLAGE,
            current_user_building_id=existing.village_id,
            subject=subject
        )
        if not db_village:
            raise BadRequestException(f"No village available for subject: {subject}")
        await self._user_village_repository.create(
            user_id=user_id,
            subject=subject,
            village_id=db_village.id,
        )
