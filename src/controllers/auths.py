from starlette.requests import Request
from starlette.responses import Response, RedirectResponse

from src.app.config import settings
from src.app.errors import BadRequestException
from src.app.uow import UoW
from src.app.utils import create_access_token, create_refresh_token
from src.repositories import UserRepository


class AuthController:
    def __init__(
            self,
            uow: UoW,
            user_repository: UserRepository,
    ):
        self.uow = uow
        self.user_repository = user_repository

    async def google_callback(
            self,
            redirect_uri: str,
            request: Request,
            response: Response,
    ):
        try:
            token = await request.state.oauth.google.authorize_access_token(request)
            user_info = token.get("userinfo") or {}
            print(user_info)
            email = user_info.get("email")
            access_token = create_access_token(
                subject=email,
                settings=settings
            )
            refresh_token = create_refresh_token(
                subject=email,
                settings=settings
            )
            db_user = await self.user_repository.get_by_email(email)
            if not db_user:
                async with self.uow:
                    await self.user_repository.create(
                        **{
                            "email": email,
                        }
                    )
            response.set_cookie("access_token", access_token)
            response.set_cookie("refresh_token", refresh_token)
            return RedirectResponse(url=redirect_uri)
        except Exception as e:
            raise BadRequestException(str(e))
