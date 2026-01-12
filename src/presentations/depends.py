import jose
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from starlette.requests import Request

from src.app.errors import UnauthorizedException
from src.app.uow import UoW
from src.app.utils import decode_token
from src.repositories import UserRepository

http_bearer = HTTPBearer()


def get_sessionmaker(request: Request) -> async_sessionmaker[AsyncSession]:
    return request.app.state.sessionmaker


async def get_session(
        sessionmaker: async_sessionmaker[AsyncSession] = Depends(get_sessionmaker),
) -> AsyncSession:
    async with sessionmaker() as session:
        yield session


async def get_uow(session: AsyncSession = Depends(get_session)) -> UoW:
    return UoW(session=session)


async def get_user_repository(session: AsyncSession = Depends(get_sessionmaker)) -> UserRepository:
    return UserRepository(session=session)


async def get_current_user(
        request: Request,
        credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
        user_repo: UserRepository = Depends(get_user_repository),
):
    if credentials is None or not credentials.credentials:
        raise UnauthorizedException("Invalid credentials")

    token = credentials.credentials
    print(token)
    try:
        decoded: dict = decode_token(
            token,
            settings=request.app.state.settings,
            expected_type="access"
        )

        user_id = decoded.get("id")
        if not user_id:
            raise UnauthorizedException("Invalid token")

        user = await user_repo.get_by_id(user_id)
        if not user:
            raise UnauthorizedException("User not found")

        return user

    except jose.ExpiredSignatureError:
        raise UnauthorizedException("Token is expired")
    except jose.JWTError:
        raise UnauthorizedException("Invalid token")
