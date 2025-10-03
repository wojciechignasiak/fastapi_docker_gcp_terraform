#3rd party libraries
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

#1st party libraries
from typing import AsyncGenerator


async def get_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(
        request.app.state.engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise