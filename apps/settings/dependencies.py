from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from apps.settings.database import async_session_maker


async def get_async_session() -> AsyncIterator[AsyncSession]:
    async with async_session_maker() as session:
        yield session
