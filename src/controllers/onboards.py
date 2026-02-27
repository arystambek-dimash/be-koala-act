import asyncio
from datetime import timezone
from typing import List, Any

from src.app.constants import SubjectEnum
from src.app.errors import BadRequestException
from src.app.passage_node_generator import PassageNodeGenerator
from src.app.uow import UoW
from src.presentations.schemas.onboards import OnboardCreate, PassageOnboard, UserLevel
from src.presentations.schemas.users import UserRead
from src.repositories import (
    BuildingRepository,
    PassageRepository,
    UserCastleRepository,
    UserRepository,
    UserVillageRepository,
    PassageNodeRepository,
    ExperienceRepository,
    WalletRepository,
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
            node_repository: PassageNodeRepository,
            node_generator: PassageNodeGenerator,
            experience_repository: ExperienceRepository,
            wallet_repository: WalletRepository,
    ):
        self._uow = uow
        self._user_repository = user_repository
        self._passage_repository = passage_repository
        self._building_repository = building_repository
        self._user_castle_repository = user_castle_repository
        self._user_village_repository = user_village_repository
        self._node_repository = node_repository
        self._node_generator = node_generator
        self._experience_repository = experience_repository
        self._wallet_repository = wallet_repository

    async def execute(self, user: UserRead, onboard: OnboardCreate) -> list:
        if user.has_onboard:
            raise BadRequestException("User has already completed onboarding")

        async with self._uow:
            # Check if castle already exists (e.g., after reset-onboard)
            existing_castle = await self._user_castle_repository.get_user_castle(user.id)
            if not existing_castle:
                db_castle = await self._building_repository.get_user_next_castle(
                    user.id
                )
                if not db_castle:
                    raise BadRequestException("No castle default template found")
                await self._user_castle_repository.create(
                    user_id=user.id,
                    castle_id=db_castle.id,
                )

            # Check if experience already exists
            existing_exp = await self._experience_repository.get_by_user_id(user.id)
            if not existing_exp:
                await self._experience_repository.create(
                    user_id=user.id,
                    level=1,
                    current_xp=0,
                )
            await self._user_repository.update(
                user.id,
                current_score=onboard.current_score,
                target_score=onboard.target_score,
                exam_date=onboard.exam_date,
                has_onboard=True,
            )

            def score_to_level(score: int) -> str:
                if score <= 1:
                    return "Bad"
                if score <= 3:
                    return "Weak"
                if score == 4:
                    return "Ok"
                return "Strong"

            results: list[dict[str, Any]] = []
            level_points: dict[UserLevel, int] = {
                UserLevel.NO_IDEA: 1,
                UserLevel.KNOW_NOT_GOOD: 3,
                UserLevel.WEAK: 4,
                UserLevel.STRONG: 5,
            }
            for subject in onboard.subjects:
                total_points = sum(
                    level_points.get(passage.user_level, 0)
                    for passage in subject.passages
                )
                normalized_score = round(total_points / max(len(subject.passages), 1))

                results.append(
                    {
                        "subject": subject.subject,
                        "score": normalized_score,
                        "level": score_to_level(normalized_score),
                    }
                )
            await self._generate_all_subjects(user.id, onboard.subjects)
            return results

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
        # Check if village for this subject already exists
        existing_villages = await self._user_village_repository.get_user_villages(user_id)
        has_subject = any(
            v.get("village_subject") == subject
            for v in existing_villages
        )

        if not has_subject:
            db_village = await self._building_repository.get_user_next_village(
                user_id,
                subject=subject,
            )
            if db_village:
                await self._user_village_repository.create(
                    user_id=user_id,
                    village_id=db_village.id,
                )

        await self._node_generator.generate(passages)
