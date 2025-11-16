import uuid
from datetime import datetime
from collections.abc import AsyncGenerator
from fastapi import Depends
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from fastapi_users.db import SQLAlchemyUserDatabase, SQLAlchemyBaseUserTableUUID


DATABASE_URL = "sqlite+aiosqlite:///./test.db"


class DeclarativeBase(DeclarativeBase):
    pass

class User(SQLAlchemyBaseUserTableUUID, DeclarativeBase):
    posts = relationship('PostModel', back_populates='user')

class PostModel(DeclarativeBase):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('user.id'))
    user = relationship('User', back_populates="posts")
    caption = Column(Text)
    url = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)



engine = create_async_engine(DATABASE_URL)

async_session = async_sessionmaker(engine, expire_on_commit=False)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(DeclarativeBase.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

async def get_user_db(session: AsyncSession = Depends(get_session)):
    yield SQLAlchemyUserDatabase(session, User)