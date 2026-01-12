from datetime import date

from src.app.constants import FundType
from src.app.errors import BadRequestException, NotFoundException
from src.app.uow import UoW
from src.app.utils import calculate_accumulated_treasure
from src.presentations.schemas.collectors import (
    CastleStatus,
    TreasureStatus,
    CollectResult,
    TapResult,
)
from src.repositories import (
    UserCastleRepository,
    WalletRepository,
)

MAX_TAPS_PER_DAY = 10
COINS_PER_TAP = 5


class CastleCollectorController:
    def __init__(
            self,
            uow: UoW,
            user_castle_repository: UserCastleRepository,
            wallet_repository: WalletRepository,
    ):
        self._uow = uow
        self._user_castle_repository = user_castle_repository
        self._wallet_repository = wallet_repository

    async def get_status(self, user_id: int) -> CastleStatus:
        user_castle = await self._user_castle_repository.get_by_user_id_with_castle(user_id)
        if not user_castle or not user_castle.castle:
            raise NotFoundException("User castle not found")

        castle = user_castle.castle
        accumulated = calculate_accumulated_treasure(
            current_amount=user_castle.treasure_amount,
            capacity=castle.treasure_capacity,
            production_rate=castle.speed_production_treasure,
            last_collect_date=user_castle.last_collect_date,
        )

        taps_remaining = await self._get_taps_remaining(user_castle)

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

    async def collect_treasure(self, user_id: int) -> CollectResult:
        user_castle = await self._user_castle_repository.get_by_user_id_with_castle(user_id)
        if not user_castle or not user_castle.castle:
            raise NotFoundException("User castle not found")

        castle = user_castle.castle

        accumulated = calculate_accumulated_treasure(
            current_amount=user_castle.treasure_amount,
            capacity=castle.treasure_capacity,
            production_rate=castle.speed_production_treasure,
            last_collect_date=user_castle.last_collect_date,
        )

        if accumulated.current_amount == 0:
            raise BadRequestException("No treasure to collect")

        async with self._uow:
            await self._user_castle_repository.update_treasure(
                user_castle.id, accumulated.current_amount
            )

            _, collected = await self._user_castle_repository.collect_treasure(user_castle.id)

            await self._wallet_repository.add_funds(
                user_id=user_id,
                amount=collected,
                fund_type=FundType.CRYSTAL,
            )

            new_balance = await self._wallet_repository.get_balance(user_id, FundType.CRYSTAL)

        return CollectResult(
            collected_amount=collected,
            fund_type=FundType.CRYSTAL,
            new_wallet_balance=new_balance,
        )

    async def tap_collect(self, user_id: int) -> TapResult:
        user_castle = await self._user_castle_repository.get_by_user_id(user_id)
        if not user_castle:
            raise NotFoundException("User castle not found")

        taps_remaining = await self._get_taps_remaining(user_castle)
        if taps_remaining <= 0:
            raise BadRequestException("No taps remaining today. Come back tomorrow!")

        async with self._uow:
            await self._user_castle_repository.record_tap(user_castle.id)

            await self._wallet_repository.add_funds(
                user_id=user_id,
                amount=COINS_PER_TAP,
                fund_type=FundType.COIN,
            )

            new_balance = await self._wallet_repository.get_balance(user_id, FundType.COIN)

        return TapResult(
            coins_collected=COINS_PER_TAP,
            taps_remaining=taps_remaining - 1,
            new_wallet_balance=new_balance,
        )

    async def _get_taps_remaining(self, user_castle) -> int:
        today = date.today()

        if user_castle.last_tap_reset_date != today:
            return MAX_TAPS_PER_DAY

        return max(0, MAX_TAPS_PER_DAY - user_castle.taps_used_today)
