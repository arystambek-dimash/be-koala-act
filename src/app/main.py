from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.api.routers.answers import router as user_answers_router
from src.api.routers.profiles import router as profile_router
from src.api.routers.roadmaps import router as roadmap_router
from src.api.routers.trainings import router as training_router
from src.api.routers.users import router as users_router
from src.app.config import Settings
from src.app.database import make_engine, make_sessionmaker


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Settings()
    app.state.settings = settings

    engine = make_engine(settings.db_url)
    app.state.engine = engine
    app.state.sessionmaker = make_sessionmaker(engine)

    async with engine.begin() as conn:
        await conn.run_sync(lambda _: None)

    yield

    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(users_router, prefix="/api")
    app.include_router(profile_router, prefix="/api")
    app.include_router(roadmap_router, prefix="/api")
    app.include_router(user_answers_router, prefix="/api")
    app.include_router(training_router, prefix="/api")

    return app


app = create_app()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
