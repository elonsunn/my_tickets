from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """For all models"""


async def create_database_engine(url: str, echo: bool) -> AsyncEngine:
    return create_async_engine(url=url, echo=echo)


async def get_db(request: Request) -> AsyncGenerator[AsyncSession]:
    async with request.app.state.sessionmaker() as session:
        yield session


DBsession = Annotated[AsyncSession, Depends(get_db)]
