from starlette.requests import Request

from src.app.config import Settings
from src.app.errors import BadRequestException
from src.app.uow import UoW
from src.app.utils import create_access_token, create_refresh_token
from src.repositories import UserRepository, ExperienceRepository


class AuthController:
    def __init__(
            self,
            uow: UoW,
            user_repository: UserRepository,
            experience_repository: ExperienceRepository = None,
    ):
        self.uow = uow
        self.user_repository = user_repository
        self.experience_repository = experience_repository

    async def google_callback(
            self,
            request: Request,
    ):
        try:
            settings = request.app.state.settings
            oauth = request.app.state.oauth

            token = await oauth.google.authorize_access_token(request)
            user_info = token.get("userinfo") or {}
            print(user_info)
            email = user_info.get("email")
            if not email:
                raise BadRequestException("Email not provided by Google")

            db_user = await self.user_repository.get_by_email(email)
            if not db_user:
                async with self.uow:
                    db_user = await self.user_repository.create(email=email, full_name=user_info.get("name"))

            access_token = create_access_token(
                subject=str(db_user.id),
                settings=settings,
                extra_claims={"id": db_user.id, "email": db_user.email}
            )
            refresh_token = create_refresh_token(
                subject=str(db_user.id),
                settings=settings,
                extra_claims={"id": db_user.id, "email": db_user.email}
            )
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "user": {
                    "id": db_user.id,
                    "email": db_user.email,
                }
            }
        except BadRequestException:
            raise
        except Exception as e:
            raise BadRequestException(f"Google authentication failed: {str(e)}")

    async def dev_login(self, email: str, settings: Settings):
        """
        DEV ONLY: Create or get user and return tokens.
        Skips OAuth, used for local frontend development.
        """
        db_user = await self.user_repository.get_by_email(email)

        if not db_user:
            async with self.uow:
                db_user = await self.user_repository.create(
                    email=email,
                    full_name=f"Dev User ({email.split('@')[0]})",
                    has_onboard=False,  # New dev users need onboarding
                )
                # Create Experience for new dev user
                if self.experience_repository:
                    await self.experience_repository.create(
                        user_id=db_user.id,
                        level=1,
                        current_xp=0,
                    )

        access_token = create_access_token(
            subject=str(db_user.id),
            settings=settings,
            extra_claims={"id": db_user.id, "email": db_user.email}
        )
        refresh_token = create_refresh_token(
            subject=str(db_user.id),
            settings=settings,
            extra_claims={"id": db_user.id, "email": db_user.email}
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user_id": db_user.id,
            "email": db_user.email,
        }
