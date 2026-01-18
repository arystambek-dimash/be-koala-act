from typing import Optional

from fastapi import Depends, Cookie
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from starlette.requests import Request

from src.app.cloudflare_r2 import CloudflareR2Service, R2Config
from src.app.errors import UnauthorizedException, ForbiddenException, TokenError
from src.app.openai_service import OpenAIService
from src.app.passage_node_generator import PassageNodeGenerator
from src.app.uow import UoW
from src.app.utils import decode_token
from src.controllers import AuthController, UserController, BuildingCollectorController
from src.controllers.building_progression import BuildingProgressionController
from src.controllers.buildings import BuildingController
from src.controllers.onboards import OnboardController
from src.controllers.passage_nodes import PassageNodeController
from src.controllers.passages import PassageController
from src.controllers.questions import QuestionController
from src.controllers.roadmaps import RoadmapController
from src.controllers.subject_onboard import SubjectOnboardController
from src.controllers.submits import SubmitController
from src.repositories import (
    UserRepository,
    BuildingRepository,
    PassageRepository,
    PassageNodeRepository,
    UserCastleRepository,
    UserNodeProgressRepository,
    UserVillageRepository,
    QuestionRepository,
    WalletRepository,
)

http_bearer = HTTPBearer(auto_error=False)


def get_sessionmaker(request: Request) -> async_sessionmaker[AsyncSession]:
    return request.app.state.sessionmaker


async def get_session(
        sessionmaker: async_sessionmaker[AsyncSession] = Depends(get_sessionmaker),
) -> AsyncSession:
    session = sessionmaker()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def get_uow(session: AsyncSession = Depends(get_session)) -> UoW:
    return UoW(session=session)


async def get_user_repository(session: AsyncSession = Depends(get_session)) -> UserRepository:
    return UserRepository(session=session)


async def get_current_user(
        request: Request,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
        access_token_cookie: Optional[str] = Cookie(default=None, alias="access_token"),
        user_repo=Depends(get_user_repository),
):
    token: Optional[str] = None
    if credentials and credentials.credentials:
        token = credentials.credentials
    elif access_token_cookie:
        token = access_token_cookie

    if not token:
        raise UnauthorizedException(
            "Missing credentials"
        )

    try:
        decoded: dict = decode_token(
            token,
            settings=request.app.state.settings,
            expected_type="access",
        )

        user_id = decoded.get("id")
        if not user_id:
            raise UnauthorizedException(
                "Invalid token payload"
            )

        user = await user_repo.get_by_id(int(user_id))
        if not user:
            raise UnauthorizedException(
                "User not found"
            )

        return user

    except TokenError:
        raise UnauthorizedException(
            "Invalid or expired token"
        )


# --- Repository factories ---
async def get_building_repository(session: AsyncSession = Depends(get_session)) -> BuildingRepository:
    return BuildingRepository(session=session)


async def get_passage_repository(session: AsyncSession = Depends(get_session)) -> PassageRepository:
    return PassageRepository(session=session)


async def get_passage_node_repository(session: AsyncSession = Depends(get_session)) -> PassageNodeRepository:
    return PassageNodeRepository(session=session)


async def get_user_castle_repository(session: AsyncSession = Depends(get_session)) -> UserCastleRepository:
    return UserCastleRepository(session=session)


async def get_user_village_repository(session: AsyncSession = Depends(get_session)) -> UserVillageRepository:
    return UserVillageRepository(session=session)


async def get_question_repository(session: AsyncSession = Depends(get_session)) -> QuestionRepository:
    return QuestionRepository(session=session)


async def get_user_node_progress_repository(
        session: AsyncSession = Depends(get_session)
) -> UserNodeProgressRepository:
    return UserNodeProgressRepository(session=session)


# --- Service factories ---

def get_openai_service(request: Request) -> OpenAIService:
    return OpenAIService(api_key=request.app.state.settings.OPENAI_API_KEY)


async def get_passage_node_generator(
        node_repository: PassageNodeRepository = Depends(get_passage_node_repository),
        openai_service: OpenAIService = Depends(get_openai_service),
) -> PassageNodeGenerator:
    return PassageNodeGenerator(
        node_repository=node_repository,
        openai_service=openai_service,
    )


# --- Controller factories ---
async def get_auth_controller(
        uow: UoW = Depends(get_uow),
        user_repo: UserRepository = Depends(get_user_repository),
):
    return AuthController(uow=uow, user_repository=user_repo)


async def get_user_controller(
        uow: UoW = Depends(get_uow),
        user_repo: UserRepository = Depends(get_user_repository),
        user_castle_repository: UserCastleRepository = Depends(get_user_castle_repository),
        user_village_repository: UserVillageRepository = Depends(get_user_village_repository)
):
    return UserController(
        uow=uow,
        user_repo=user_repo,
        castle_repository=user_castle_repository,
        village_repository=user_village_repository
    )


async def get_onboard_controller(
        uow: UoW = Depends(get_uow),
        user_repository: UserRepository = Depends(get_user_repository),
        passage_repository: PassageRepository = Depends(get_passage_repository),
        building_repository: BuildingRepository = Depends(get_building_repository),
        user_castle_repository: UserCastleRepository = Depends(get_user_castle_repository),
        user_village_repository: UserVillageRepository = Depends(get_user_village_repository),
        node_generator: PassageNodeGenerator = Depends(get_passage_node_generator),
) -> OnboardController:
    return OnboardController(
        uow=uow,
        user_repository=user_repository,
        passage_repository=passage_repository,
        building_repository=building_repository,
        user_castle_repository=user_castle_repository,
        user_village_repository=user_village_repository,
        node_generator=node_generator,
    )


async def get_subject_onboard_controller(
        uow: UoW = Depends(get_uow),
        user_village_repository: UserVillageRepository = Depends(get_user_village_repository),
        node_repository: PassageNodeRepository = Depends(get_passage_node_repository),
        node_generator: PassageNodeGenerator = Depends(get_passage_node_generator),
        building_repository: BuildingRepository = Depends(get_building_repository),
) -> SubjectOnboardController:
    return SubjectOnboardController(
        uow=uow,
        user_village_repository=user_village_repository,
        node_repository=node_repository,
        node_generator=node_generator,
        building_repository=building_repository
    )


async def get_roadmap_controller(
        uow: UoW = Depends(get_uow),
        passage_repository: PassageRepository = Depends(get_passage_repository),
        node_repository: PassageNodeRepository = Depends(get_passage_node_repository),
        village_repository: UserVillageRepository = Depends(get_user_village_repository),
        question_repository: QuestionRepository = Depends(get_question_repository),
        progress_repository: UserNodeProgressRepository = Depends(get_user_node_progress_repository),
        openai_service: OpenAIService = Depends(get_openai_service),
) -> RoadmapController:
    return RoadmapController(
        uow=uow,
        passage_repository=passage_repository,
        node_repository=node_repository,
        village_repository=village_repository,
        question_repository=question_repository,
        progress_repository=progress_repository,
        openai_service=openai_service,
    )


# --- Auth dependencies ---
async def require_admin(
        current_user=Depends(get_current_user),
):
    if not current_user.is_admin:
        raise ForbiddenException("Admin access required")
    return current_user


# --- Additional repository factories ---
async def get_wallet_repository(session: AsyncSession = Depends(get_session)) -> WalletRepository:
    return WalletRepository(session=session)


# --- Service factories ---
def get_cloudflare_r2_service(request: Request) -> CloudflareR2Service:
    config = R2Config(
        account_id=request.app.state.settings.CLOUDFLARE_ACCOUNT_ID,
        access_key_id=request.app.state.settings.CLOUDFLARE_ACCESS_KEY_ID,
        secret_access_key=request.app.state.settings.CLOUDFLARE_SECRET_KEY_ID,
        bucket_name=request.app.state.settings.CLOUDFLARE_BUCKET_NAME,
    )
    return CloudflareR2Service(cfg=config)


async def get_building_progression_controller(
        uow: UoW = Depends(get_uow),
        user_castle_repository: UserCastleRepository = Depends(get_user_castle_repository),
        user_village_repository: UserVillageRepository = Depends(get_user_village_repository),
        wallet_repository: WalletRepository = Depends(get_wallet_repository),
        building_repository: BuildingRepository = Depends(get_building_repository),
) -> BuildingProgressionController:
    return BuildingProgressionController(
        uow=uow,
        user_castle_repository=user_castle_repository,
        user_village_repository=user_village_repository,
        wallet_repository=wallet_repository,
        building_repository=building_repository,
    )


# --- Content controller factories (public read access) ---
async def get_building_controller(
        uow: UoW = Depends(get_uow),
        building_repository: BuildingRepository = Depends(get_building_repository),
        cloudflare_r2: CloudflareR2Service = Depends(get_cloudflare_r2_service),
        passage_repository: PassageRepository = Depends(get_passage_repository),
        user_village_repository: UserVillageRepository = Depends(get_user_village_repository),
        user_castle_repository: UserCastleRepository = Depends(get_user_castle_repository),
) -> BuildingController:
    return BuildingController(
        uow=uow,
        building_repository=building_repository,
        cloudflare_r2=cloudflare_r2,
        passage_repository=passage_repository,
        user_village_repository=user_village_repository,
        user_castle_repository=user_castle_repository,
    )


async def get_passage_controller(
        uow: UoW = Depends(get_uow),
        passage_repository: PassageRepository = Depends(get_passage_repository),
        building_repository: BuildingRepository = Depends(get_building_repository),
) -> PassageController:
    return PassageController(
        uow=uow,
        passage_repository=passage_repository,
        building_repository=building_repository,
    )


async def get_passage_node_controller(
        uow: UoW = Depends(get_uow),
        node_repository: PassageNodeRepository = Depends(get_passage_node_repository),
        passage_repository: PassageRepository = Depends(get_passage_repository),
) -> PassageNodeController:
    return PassageNodeController(
        uow=uow,
        node_repository=node_repository,
        passage_repository=passage_repository,
    )


async def get_building_collector_controller(
        uow: UoW = Depends(get_uow),
        user_castle_repository: UserCastleRepository = Depends(get_user_castle_repository),
        wallet_repository: WalletRepository = Depends(get_wallet_repository),
        user_village_repository: UserVillageRepository = Depends(get_user_village_repository),
) -> BuildingCollectorController:
    return BuildingCollectorController(
        uow=uow,
        user_castle_repository=user_castle_repository,
        wallet_repository=wallet_repository,
        user_village_repository=user_village_repository,
    )


async def get_question_controller(
        uow: UoW = Depends(get_uow),
        question_repository: QuestionRepository = Depends(get_question_repository),
        node_repository: PassageNodeRepository = Depends(get_passage_node_repository),
) -> QuestionController:
    return QuestionController(
        uow=uow,
        question_repository=question_repository,
        node_repository=node_repository,
    )


async def get_submit_controller(
        uow: UoW = Depends(get_uow),
        question_repository: QuestionRepository = Depends(get_question_repository),
        node_repository: PassageNodeRepository = Depends(get_passage_node_repository),
        user_progress_repository: UserNodeProgressRepository = Depends(get_user_node_progress_repository),
) -> SubmitController:
    return SubmitController(
        uow=uow,
        question_repository=question_repository,
        node_repository=node_repository,
        user_progress_repository=user_progress_repository,
    )