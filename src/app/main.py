from contextlib import asynccontextmanager

from authlib.integrations.starlette_client import OAuth
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.app.config import Settings
from src.app.database import make_engine, make_sessionmaker


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Settings()
    app.state.settings = settings

    engine = make_engine(settings.db_url)
    app.state.engine = engine
    app.state.sessionmaker = make_sessionmaker(engine)

    oauth = OAuth()
    oauth.register(
        name="google",
        client_id=app.state.settings.GOOGLE_CLIENT_ID,
        client_secret=app.state.settings.GOOGLE_CLIENT_SECRET,
        authorize_url="https://accounts.google.com/o/oauth2/auth",
        authorize_params={"scope": "openid email profile"},
        access_token_url="https://oauth2.googleapis.com/token",
        client_kwargs={"scope": "openid email profile"},
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration"
    )

    app.state.oauth = oauth


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    return app


app = create_app()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
