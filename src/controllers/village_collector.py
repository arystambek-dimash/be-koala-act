from src.app.constants import FundType, SubjectEnum
from src.app.errors import BadRequestException, NotFoundException
from src.app.uow import UoW
from src.app.utils import calculate_accumulated_treasure
from src.presentations.schemas.collectors import (
    VillageStatus,
    TreasureStatus,
    CollectResult,
)
from src.repositories import (
    UserVillageRepository,
    WalletRepository,
)


class VillageCollectorController:
    def __init__(
            self,
            uow: UoW,
            user_village_repository: UserVillageRepository,
            wallet_repository: WalletRepository,
    ):
        self._uow = uow
        self._user_village_repository = user_village_repository
        self._wallet_repository = wallet_repository

    async def get_status(self, user_id: int, subject: SubjectEnum) -> VillageStatus:
        user_village = await self._user_village_repository.get_by_user_and_subject_with_village(
            user_id, subject
        )
        if not user_village or not user_village.village:
            raise NotFoundException(f"User village for {subject} not found")

        village = user_village.village

        accumulated = calculate_accumulated_treasure(
            current_amount=user_village.treasure_amount,
            capacity=village.treasure_capacity,
            production_rate=village.speed_production_treasure,
            last_collect_date=user_village.last_collect_date,
        )

        return VillageStatus(
            village_id=village.id,
            village_title=village.title,
            subject=subject,
            treasure=TreasureStatus(
                current_amount=accumulated.current_amount,
                capacity=village.treasure_capacity,
                production_rate=village.speed_production_treasure,
                last_collect_date=user_village.last_collect_date,
                time_to_full_minutes=accumulated.time_to_full_minutes,
                fund_type=FundType.COIN,
            ),
        )

    async def get_all_statuses(self, user_id: int) -> list[VillageStatus]:
        user_villages = await self._user_village_repository.get_by_user_id_with_villages(user_id)

        statuses = []
        for user_village in user_villages:
            if not user_village.village:
                continue

            village = user_village.village
            accumulated = calculate_accumulated_treasure(
                current_amount=user_village.treasure_amount,
                capacity=village.treasure_capacity,
                production_rate=village.speed_production_treasure,
                last_collect_date=user_village.last_collect_date,
            )

            statuses.append(VillageStatus(
                village_id=village.id,
                village_title=village.title,
                subject=user_village.subject,
                treasure=TreasureStatus(
                    current_amount=accumulated.current_amount,
                    capacity=village.treasure_capacity,
                    production_rate=village.speed_production_treasure,
                    last_collect_date=user_village.last_collect_date,
                    time_to_full_minutes=accumulated.time_to_full_minutes,
                    fund_type=FundType.COIN,
                ),
            ))

        return statuses

    async def collect_treasure(self, user_id: int, subject: SubjectEnum) -> CollectResult:
        user_village = await self._user_village_repository.get_by_user_and_subject_with_village(
            user_id, subject
        )
        if not user_village or not user_village.village:
            raise NotFoundException(f"User village for {subject} not found")

        village = user_village.village

        accumulated = calculate_accumulated_treasure(
            current_amount=user_village.treasure_amount,
            capacity=village.treasure_capacity,
            production_rate=village.speed_production_treasure,
            last_collect_date=user_village.last_collect_date,
        )

        if accumulated.current_amount == 0:
            raise BadRequestException("No treasure to collect")

        async with self._uow:
            await self._user_village_repository.update_treasure(
                user_village.id,
                accumulated.current_amount
            )

            _, collected = await self._user_village_repository.collect_treasure(user_village.id)

            await self._wallet_repository.add_funds(
                user_id=user_id,
                amount=collected,
                fund_type=FundType.COIN,
            )

            new_balance = await self._wallet_repository.get_balance(user_id, FundType.COIN)

        return CollectResult(
            collected_amount=collected,
            fund_type=FundType.COIN,
            new_wallet_balance=new_balance,
        )
