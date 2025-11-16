from pydantic import BaseModel
from fastapi_users.schemas import BaseUserCreate, BaseUserUpdate, BaseUser
import uuid


class PostModel(BaseModel):
    title: str
    content: str


class UserCreate(BaseUserCreate):
    pass

class UserUpdate(BaseUserUpdate):
    pass

class UserRead(BaseUser[uuid.UUID]):
    pass