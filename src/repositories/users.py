from sqlalchemy import select

from src.models.users import User
from src.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def set_onboard_complete(self, user_id: int) -> User | None:
        user = await self.get_by_id(user_id)
        if not user:
            return None
        user.has_onboard = True
        await self._session.flush()
        return user
