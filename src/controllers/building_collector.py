from dataclasses import dataclass
from datetime import datetime, timezone, date
from typing import Optional

from src.app.constants import FundType
from src.app.errors import BadRequestException, NotFoundException
from src.app.uow import UoW
from src.presentations.schemas.collectors import (
    CastleStatus,
    VillageStatus,
    TreasureStatus,
    CollectResult,
    TapResult,
)
from src.repositories import (
    UserCastleRepository,
    UserVillageRepository,
    WalletRepository
)

MAX_TAPS_PER_DAY = 10
COINS_PER_TAP = 5


@dataclass
class AccumulatedTreasure:
    current_amount: int
    time_to_full_minutes: int


class BuildingCollectorController:
    def __init__(
            self,
            uow: UoW,
            user_castle_repository: UserCastleRepository,
            user_village_repository: UserVillageRepository,
            wallet_repository: WalletRepository,
    ):
        self._uow = uow
        self._user_castle_repository = user_castle_repository
        self._user_village_repository = user_village_repository
        self._wallet_repository = wallet_repository

    # --------- PUBLIC API ---------
    async def get_status_castle(self, user_id: int) -> CastleStatus:
        user_castle, castle = await self._get_user_castle_with_entity(user_id)
        accumulated = self._calculate_accumulated_treasure(
            current_amount=user_castle.treasure_amount,
            capacity=castle.treasure_capacity,
            production_rate=castle.speed_production_treasure,
            last_collect_date=user_castle.last_collect_date,
        )
        taps_remaining = self._get_taps_remaining(user_castle)

        return CastleStatus(
            castle_id=castle.id,
            castle_title=castle.title,
            treasure=TreasureStatus(
                current_amount=accumulated.current_amount,
                capacity=castle.treasure_capacity,
                production_rate=castle.speed_production_treasure,
                last_collect_date=user_castle.last_collect_date,
                time_to_full_minutes=accumulated.time_to_full_minutes,
                fund_type=FundType.CRYSTAL,
            ),
            taps_remaining=taps_remaining,
            max_taps_per_day=MAX_TAPS_PER_DAY,
            coins_per_tap=COINS_PER_TAP,
        )

    async def get_status_village(self, user_id: int, village_id: int) -> VillageStatus:
        user_village, village = await self._get_user_village_with_entity(user_id, village_id)
        accumulated = self._calculate_accumulated_treasure(
            current_amount=user_village.treasure_amount,
            capacity=village.treasure_capacity,
            production_rate=village.speed_production_treasure,
            last_collect_date=user_village.last_collect_date,
        )

        return VillageStatus(
            village_id=village.id,
            village_title=village.title,
            subject=village.subject,
            treasure=TreasureStatus(
                current_amount=accumulated.current_amount,
                capacity=village.treasure_capacity,
                production_rate=village.speed_production_treasure,
                last_collect_date=user_village.last_collect_date,
                time_to_full_minutes=accumulated.time_to_full_minutes,
                fund_type=FundType.COIN,
            ),
        )

    async def collect_treasure_castle(self, user_id: int) -> CollectResult:
        user_castle, castle = await self._get_user_castle_with_entity(user_id)

        return await self._collect_treasure_generic(
            user_id=user_id,
            current_amount=user_castle.treasure_amount,
            capacity=castle.treasure_capacity,
            production_rate=castle.speed_production_treasure,
            last_collect_date=user_castle.last_collect_date,
            fund_type=FundType.CRYSTAL,
            update_treasure=lambda amount: self._user_castle_repository.update_treasure(user_castle.id, amount),
            collect=lambda: self._user_castle_repository.collect_treasure(user_castle.id),
            get_balance=lambda: self._wallet_repository.get_balance(user_id, FundType.CRYSTAL),
        )

    async def collect_treasure_village(self, user_id: int, village_id: int) -> CollectResult:
        user_village, village = await self._get_user_village_with_entity(user_id, village_id)

        return await self._collect_treasure_generic(
            user_id=user_id,
            current_amount=user_village.treasure_amount,
            capacity=village.treasure_capacity,
            production_rate=village.speed_production_treasure,
            last_collect_date=user_village.last_collect_date,
            fund_type=FundType.COIN,  # ✅ деревня -> COIN
            update_treasure=lambda amount: self._user_village_repository.update_treasure(user_village.id, amount),
            collect=lambda: self._user_village_repository.collect_treasure(user_village.id),  # ✅ village repo
            get_balance=lambda: self._wallet_repository.get_balance(user_id, FundType.COIN),
        )

    async def tap_collect(self, user_id: int, tapped: int = 1) -> TapResult:
        user_castle = await self._user_castle_repository.get_by_user_id(user_id)
        if not user_castle:
            raise NotFoundException("User castle not found")

        taps_remaining = self._get_taps_remaining(user_castle)
        if taps_remaining <= 0:
            raise BadRequestException("No taps remaining today. Come back tomorrow!")

        actual_taps = min(max(1, tapped), taps_remaining)
        total_coins = actual_taps * COINS_PER_TAP

        async with self._uow:
            await self._user_castle_repository.record_taps(user_castle.id, count=actual_taps)
            await self._wallet_repository.add_funds(
                user_id=user_id,
                amount=total_coins,
                fund_type=FundType.COIN,
            )
            new_balance = await self._wallet_repository.get_balance(user_id, FundType.COIN)

        return TapResult(
            coins_collected=total_coins,
            taps_remaining=taps_remaining - actual_taps,
            new_wallet_balance=new_balance,
        )

    # --------- DRY HELPERS ---------
    async def _get_user_castle_with_entity(self, user_id: int):
        user_castle = await self._user_castle_repository.get_by_user_id_with_castle(user_id)
        if not user_castle:
            raise NotFoundException("User castle not found")
        return user_castle, user_castle.castle

    async def _get_user_village_with_entity(self, user_id: int, village_id: int):
        user_village = await self._user_village_repository.get_by_user_and_village(user_id, village_id)
        if not user_village:
            raise NotFoundException(f"User village for {village_id} not found")
        return user_village, user_village.village

    async def _collect_treasure_generic(
            self,
            *,
            user_id: int,
            current_amount: int,
            capacity: int,
            production_rate: int,
            last_collect_date: Optional[datetime],
            fund_type: FundType,
            update_treasure,
            collect,
            get_balance,
    ) -> CollectResult:
        accumulated = self._calculate_accumulated_treasure(
            current_amount=current_amount,
            capacity=capacity,
            production_rate=production_rate,
            last_collect_date=last_collect_date,
        )

        if accumulated.current_amount <= 0:
            raise BadRequestException("No treasure to collect")

        async with self._uow:
            await update_treasure(accumulated.current_amount)

            _, collected = await collect()

            await self._wallet_repository.add_funds(
                user_id=user_id,
                amount=collected,
                fund_type=fund_type,
            )
            new_balance = await get_balance()

        return CollectResult(
            collected_amount=collected,
            fund_type=fund_type,
            new_wallet_balance=new_balance,
        )

    def _utc_today(self) -> date:
        return datetime.now(timezone.utc).date()

    def _get_taps_remaining(self, user_castle) -> int:
        today = self._utc_today()

        if user_castle.last_tap_reset_date != today:
            return MAX_TAPS_PER_DAY

        return max(0, MAX_TAPS_PER_DAY - user_castle.taps_used_today)

    def _calculate_accumulated_treasure(
            self,
            current_amount: int,
            capacity: int,
            production_rate: int,
            last_collect_date: Optional[datetime],
    ) -> AccumulatedTreasure:
        if production_rate <= 0:
            return AccumulatedTreasure(current_amount=min(current_amount, capacity), time_to_full_minutes=0)

        current_amount = max(0, min(current_amount, capacity))

        if last_collect_date is None:
            remaining = capacity - current_amount
            return AccumulatedTreasure(
                current_amount=current_amount,
                time_to_full_minutes=int(remaining / production_rate * 60) if remaining > 0 else 0,
            )

        now = datetime.now(timezone.utc)
        hours_elapsed = max(0.0, (now - last_collect_date).total_seconds() / 3600.0)

        generated = int(production_rate * hours_elapsed)
        new_amount = min(current_amount + generated, capacity)

        remaining_capacity = capacity - new_amount
        time_to_full = int(remaining_capacity / production_rate * 60) if remaining_capacity > 0 else 0

        return AccumulatedTreasure(current_amount=new_amount, time_to_full_minutes=time_to_full)

    async def get_all_villages_statuses(self, user_id: int) -> list[VillageStatus]:
        user_villages = await self._user_village_repository.get_user_villages(user_id)

        result: list[VillageStatus] = []
        for uv in user_villages:
            village = uv.village
            accumulated = self._calculate_accumulated_treasure(
                current_amount=uv.treasure_amount,
                capacity=village.treasure_capacity,
                production_rate=village.speed_production_treasure,
                last_collect_date=uv.last_collect_date,
            )
            result.append(
                VillageStatus(
                    village_id=village.id,
                    village_title=village.title,
                    subject=village.subject,
                    treasure=TreasureStatus(
                        current_amount=accumulated.current_amount,
                        capacity=village.treasure_capacity,
                        production_rate=village.speed_production_treasure,
                        last_collect_date=uv.last_collect_date,
                        time_to_full_minutes=accumulated.time_to_full_minutes,
                        fund_type=FundType.COIN,
                    ),
                )
            )
        return result
