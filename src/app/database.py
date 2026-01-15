from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


def make_engine(db_uri: str) -> AsyncEngine:
    return create_async_engine(
        db_uri,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )


def make_sessionmaker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        engine,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
        class_=AsyncSession,
    )


class Base(DeclarativeBase):
    __abstract__ = True
