from contextlib import asynccontextmanager

from authlib.integrations.starlette_client import OAuth
from fastapi import FastAPI, APIRouter, HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request

from src.app.config import settings
from src.app.database import make_engine, make_sessionmaker
from src.app.errors import BaseError
from src.presentations.routers import (
    auth,
    buildings,
    collectors,
    nodes,
    onboards,
    passages,
    progression,
    questions,
    roadmaps,
    users,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.settings = settings

    engine = make_engine(settings.db_url)
    app.state.engine = engine
    app.state.sessionmaker = make_sessionmaker(engine)

    oauth = OAuth()
    oauth.register(
        name="google",
        client_id=app.state.settings.GOOGLE_CLIENT_ID,
        client_secret=app.state.settings.GOOGLE_CLIENT_SECRET,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={
            "scope": "openid email profile",
            "timeout": 10.0,
        },
    )
    app.state.oauth = oauth

    yield


def create_app() -> FastAPI:
    v1_api = APIRouter(prefix="/api/v1")
    # Auth & User routers
    v1_api.include_router(auth.router)
    v1_api.include_router(users.router)
    v1_api.include_router(onboards.router)

    # Game mechanics routers
    v1_api.include_router(collectors.router)
    v1_api.include_router(progression.router)
    v1_api.include_router(roadmaps.router)

    # Content management routers (Admin + Public read)
    v1_api.include_router(buildings.router)
    v1_api.include_router(passages.router)
    v1_api.include_router(nodes.router)
    v1_api.include_router(questions.router)

    app = FastAPI(lifespan=lifespan, swagger_ui_parameters={"withCredentials": True})
    app.include_router(v1_api)
    return app


app = create_app()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    same_site="lax" if settings.DEBUG else "none",
    https_only=False if settings.DEBUG else True,
)


@app.exception_handler(BaseError)
async def bad_request_handler(_: Request, exc: BaseError):
    raise HTTPException(status_code=exc.status_code, detail=exc.message)
