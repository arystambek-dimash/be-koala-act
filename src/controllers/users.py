from src.app.errors import NotFoundException
from src.app.uow import UoW
from src.presentations.schemas.users import UserUpdate, UserRead
from src.repositories import UserRepository


class UserController:
    def __init__(
            self,
            uow: UoW,
            user_repo: UserRepository,
    ):
        self.uow = uow
        self.user_repo = user_repo

    async def profile_update(self, user_id: int, data: UserUpdate):
        try:
            db_user = await self.user_repo.get_by_id(user_id)
            if not db_user:
                raise NotFoundException("User not found")
            async with self.uow:
                updated = await self.user_repo.update(user_id, **data.dict(exclude_unset=True))
            return UserRead.from_orm(updated)
        except Exception as e:
            raise e
