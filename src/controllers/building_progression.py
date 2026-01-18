from src.app.constants import FundType, SubjectEnum
from src.app.errors import BadRequestException, NotFoundException
from src.app.uow import UoW
from src.presentations.schemas.collectors import UpgradeInfo, UpgradeResult
from src.repositories import (
    UserCastleRepository,
    UserVillageRepository,
    WalletRepository, BuildingRepository,
)

CASTLE_UPGRADE_FUND_TYPE = FundType.CRYSTAL
VILLAGE_UPGRADE_FUND_TYPE = FundType.COIN


class BuildingProgressionController:
    def __init__(
            self,
            uow: UoW,
            user_castle_repository: UserCastleRepository,
            user_village_repository: UserVillageRepository,
            building_repository: BuildingRepository,
            wallet_repository: WalletRepository,
    ):
        self._uow = uow
        self._user_castle_repository = user_castle_repository
        self._user_village_repository = user_village_repository
        self._building_repository = building_repository
        self._wallet_repository = wallet_repository

    async def get_castle_upgrade_info(self, user_id: int) -> UpgradeInfo:
        user_castle_data = await self._user_castle_repository.get_user_castle(user_id)
        if not user_castle_data:
            raise NotFoundException("User castle not found")

        current_level = user_castle_data.get("castle_id")
        next_castle = await self._building_repository.get_user_next_castle(user_id)
        balance = await self._wallet_repository.get_balance(
            user_id,
            CASTLE_UPGRADE_FUND_TYPE
        )

        if not next_castle:
            return UpgradeInfo(
                can_upgrade=False,
                current_level=current_level,
                next_level=None,
                upgrade_cost=None,
                cost_fund_type=CASTLE_UPGRADE_FUND_TYPE,
                current_balance=balance,
                reason="Already at maximum castle level",
            )

        upgrade_cost = next_castle.cost or 0
        can_afford = balance >= upgrade_cost

        return UpgradeInfo(
            can_upgrade=can_afford,
            current_level=current_level,
            next_level=next_castle.id,
            upgrade_cost=upgrade_cost,
            cost_fund_type=CASTLE_UPGRADE_FUND_TYPE,
            current_balance=balance,
            reason=None if can_afford else f"Insufficient {CASTLE_UPGRADE_FUND_TYPE.value}. Need {upgrade_cost}, have {balance}",
        )

    async def upgrade_castle(self, user_id: int) -> UpgradeResult:
        user_castle_data = await self._user_castle_repository.get_user_castle(user_id)
        if not user_castle_data:
            raise NotFoundException("User castle not found")

        next_castle = await self._building_repository.get_user_next_castle(user_id)
        if not next_castle:
            raise BadRequestException("Already at maximum castle level")

        upgrade_cost = next_castle.cost or 0
        balance = await self._wallet_repository.get_balance(user_id, CASTLE_UPGRADE_FUND_TYPE)
        if balance < upgrade_cost:
            raise BadRequestException(
                f"Insufficient {CASTLE_UPGRADE_FUND_TYPE.value}. "
                f"Need {upgrade_cost}, have {balance}"
            )

        async with self._uow:
            if upgrade_cost > 0:
                await self._wallet_repository.deduct_funds(
                    user_id=user_id,
                    amount=upgrade_cost,
                    fund_type=CASTLE_UPGRADE_FUND_TYPE,
                )

            await self._user_castle_repository.upgrade_castle(
                user_castle_id=user_castle_data.get("user_castle_id"),
                new_castle_id=next_castle.id,
            )

            new_balance = await self._wallet_repository.get_balance(user_id, CASTLE_UPGRADE_FUND_TYPE)

        return UpgradeResult(
            success=True,
            new_level=next_castle.id,
            cost_paid=upgrade_cost,
            new_balance=new_balance,
        )

    async def get_village_upgrade_info(self, user_id: int, subject: SubjectEnum) -> UpgradeInfo:
        user_villages = await self._user_village_repository.get_user_villages(user_id)
        user_village = None
        for v in user_villages:
            if v.get("village_subject") == subject:
                user_village = v
                break

        if not user_village:
            raise NotFoundException(f"User village for {subject} not found")

        current_level = user_village.get("village_id")
        next_village = await self._building_repository.get_user_next_village(user_id, subject)

        balance = await self._wallet_repository.get_balance(user_id, VILLAGE_UPGRADE_FUND_TYPE)

        if not next_village:
            return UpgradeInfo(
                can_upgrade=False,
                current_level=current_level,
                next_level=None,
                upgrade_cost=None,
                cost_fund_type=VILLAGE_UPGRADE_FUND_TYPE,
                current_balance=balance,
                reason="Already at maximum village level",
            )

        upgrade_cost = next_village.cost or 0
        can_afford = balance >= upgrade_cost

        return UpgradeInfo(
            can_upgrade=can_afford,
            current_level=current_level,
            next_level=next_village.id,
            upgrade_cost=upgrade_cost,
            cost_fund_type=VILLAGE_UPGRADE_FUND_TYPE,
            current_balance=balance,
            reason=None if can_afford else f"Insufficient {VILLAGE_UPGRADE_FUND_TYPE.value}. Need {upgrade_cost}, have {balance}",
        )

    async def upgrade_village(self, user_id: int, subject: SubjectEnum) -> UpgradeResult:
        user_villages = await self._user_village_repository.get_user_villages(user_id)
        user_village = None
        for v in user_villages:
            if v.get("village_subject") == subject:
                user_village = v
                break

        if not user_village:
            raise NotFoundException(f"User village for {subject} not found")

        next_village = await self._building_repository.get_user_next_village(user_id, subject)
        if not next_village:
            raise BadRequestException(f"Already at maximum village level for {subject}")

        upgrade_cost = next_village.cost or 0

        balance = await self._wallet_repository.get_balance(user_id, VILLAGE_UPGRADE_FUND_TYPE)
        if balance < upgrade_cost:
            raise BadRequestException(
                f"Insufficient {VILLAGE_UPGRADE_FUND_TYPE.value}. "
                f"Need {upgrade_cost}, have {balance}"
            )

        async with self._uow:
            if upgrade_cost > 0:
                await self._wallet_repository.deduct_funds(
                    user_id=user_id,
                    amount=upgrade_cost,
                    fund_type=VILLAGE_UPGRADE_FUND_TYPE,
                )

            await self._user_village_repository.upgrade_village(
                user_village_id=user_village.get("user_village_id"),
                new_village_id=next_village.id,
            )

            new_balance = await self._wallet_repository.get_balance(user_id, VILLAGE_UPGRADE_FUND_TYPE)

        return UpgradeResult(
            success=True,
            new_level=next_village.id,
            cost_paid=upgrade_cost,
            new_balance=new_balance,
        )
