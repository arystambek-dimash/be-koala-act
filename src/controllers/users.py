from src.app.errors import NotFoundException
from src.app.uow import UoW
from src.presentations.schemas.users import UserUpdate, UserRead, UserCastleWithVillages, UserVillageRead
from src.repositories import UserRepository, UserCastleRepository, UserVillageRepository


class UserController:
    def __init__(
            self,
            uow: UoW,
            user_repo: UserRepository,
            castle_repository: UserCastleRepository,
            village_repository: UserVillageRepository,
    ):
        self.uow = uow
        self.user_repo = user_repo
        self.castle_repository = castle_repository
        self.village_repository = village_repository

    async def profile_update(self, user_id: int, data: UserUpdate):
        try:
            db_user = await self.user_repo.get_by_id(user_id)
            if not db_user:
                raise NotFoundException("User not found")
            async with self.uow:
                updated = await self.user_repo.update(user_id, **data.model_dump(exclude_unset=True))
            return UserRead.model_validate(updated)
        except Exception as e:
            raise e

    async def get_user_buildings(self, user_id: int):
        user_castle = await self.castle_repository.get_user_castle(user_id)
        if not user_castle:
            raise NotFoundException("User castle is not found")

        user_villages = await self.village_repository.get_user_villages(user_id)
        villages = [UserVillageRead.model_validate(village) for village in user_villages]
        return UserCastleWithVillages(
            id=user_castle.get("user_castle_id"),
            svg=user_castle.get("castle_svg"),
            treasure_amount=user_castle.get("treasure_amount"),
            last_collect_date=user_castle.get("last_collect_date"),
            taps_used_today=user_castle.get("taps_used_today"),
            last_tap_reset_date=user_castle.get("last_tap_reset_date"),
            speed_production_treasure=user_castle.get("speed_production_treasure"),
            villages=villages,
        )
