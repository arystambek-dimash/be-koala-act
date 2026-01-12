import asyncio
from typing import List

from src.app.constants import SubjectEnum
from src.app.errors import BadRequestException
from src.app.passage_node_generator import PassageNodeGenerator
from src.app.uow import UoW
from src.presentations.schemas.onboards import OnboardCreate, PassageOnboard
from src.presentations.schemas.users import UserRead
from src.repositories import (
    BuildingRepository,
    PassageRepository,
    UserCastleRepository,
    UserRepository,
    UserVillageRepository,
)


class OnboardController:
    def __init__(
            self,
            uow: UoW,
            user_repository: UserRepository,
            passage_repository: PassageRepository,
            building_repository: BuildingRepository,
            user_castle_repository: UserCastleRepository,
            user_village_repository: UserVillageRepository,
            node_generator: PassageNodeGenerator,
    ):
        self._uow = uow
        self._user_repository = user_repository
        self._passage_repository = passage_repository
        self._building_repository = building_repository
        self._user_castle_repository = user_castle_repository
        self._user_village_repository = user_village_repository
        self._node_generator = node_generator

    async def execute(self, user: UserRead, onboard: OnboardCreate) -> None:
        if user.has_onboard:
            raise BadRequestException("User has already completed onboarding")

        async with self._uow:
            await self._setup_castle(user.id)
            await self._update_user_profile(user.id, onboard)
            await self._generate_all_subjects(user.id, onboard.subjects)

    async def _setup_castle(self, user_id: int) -> None:
        db_castle = await self._user_castle_repository.get_user_next_castle(user_id)
        if not db_castle:
            raise BadRequestException("No castle available for user")

        await self._user_castle_repository.create(
            user_id=user_id,
            castle_id=db_castle.id,
        )

    async def _update_user_profile(self, user_id: int, onboard: OnboardCreate) -> None:
        await self._user_repository.update(
            user_id,
            current_score=onboard.current_score,
            target_score=onboard.target_score,
            exam_date=onboard.exam_date,
            has_onboard=True,
        )

    async def _generate_all_subjects(self, user_id: int, subjects: list) -> None:
        await asyncio.gather(
            *[
                self._generate_subject_roadmap(
                    subject=subject.subject,
                    passages=subject.passages,
                    user_id=user_id,
                )
                for subject in subjects
            ]
        )

    async def _generate_subject_roadmap(
            self,
            subject: SubjectEnum,
            passages: List[PassageOnboard],
            user_id: int,
    ) -> None:
        await self._ensure_village_exists(user_id, subject)
        await self._node_generator.generate(passages, user_id)

    async def _ensure_village_exists(self, user_id: int, subject: SubjectEnum) -> None:
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
