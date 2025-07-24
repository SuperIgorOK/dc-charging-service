from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy.pool import NullPool

from apps.settings.config import get_settings


def get_engine():
    settings = get_settings()

    if settings.MODE == "TEST":
        url = settings.TEST_DATABASE_URL
        params = {"poolclass": NullPool}
    else:
        url = settings.DATABASE_URL
        params = {}

    return url, params


database_url, database_params = get_engine()
engine = create_async_engine(database_url, **database_params)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"


@asynccontextmanager
async def get_session_context() -> AsyncIterator[AsyncSession]:
    async with async_session_maker() as session:
        yield session
