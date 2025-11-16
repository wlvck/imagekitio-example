from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from src.db import create_db_and_tables, get_session, PostModel, User
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
from src.users import current_active_user, fastapi_users, auth_backend
from src.images import imagekit
from src.schemas import UserRead, UserUpdate, UserCreate
import uuid
import shutil
import os
import tempfile

@asynccontextmanager
async def lifespan(instance: FastAPI):
    await create_db_and_tables()
    yield


instance = FastAPI(lifespan=lifespan)

instance.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)
instance.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
instance.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
instance.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
instance.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


@instance.post("/post")
async def create_post(
    file: UploadFile = File(...),
    caption: str = Form(...),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_session)
):
    temp_file_path = None

    try: 
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name

        upload_options = UploadFileRequestOptions(
            use_unique_file_name=True,
            tags=["post_image"]
        )

        upload_result = imagekit.upload_file(
            file=open(temp_file_path, "rb"),
            file_name=file.filename,
            options=upload_options
        )

        if upload_result.response_metadata.http_status_code != 200:
            raise HTTPException(status_code=500, detail="Image upload failed")
        
        post = PostModel(
            caption=caption,
            user_id=user.id,
            url=upload_result.url,
            file_type="video" if file.content_type.startswith("video/") else "image",
            file_name=upload_result.name
        )
        session.add(post)

        await session.commit()
        await session.refresh(post)
        return post
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {str(e)}")
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        file.file.close()


@instance.get("/posts")
async def get_posts(session: AsyncSession = Depends(get_session), user: User = Depends(current_active_user),):
    result = await session.execute(
        select(PostModel).order_by(PostModel.created_at.desc())
    )

    posts = [row[0] for row in result.all()]
    
    result = await session.execute(
        select(User).where(User.id == user.id)
    )
    user_email = result.scalar_one().email

    posts_data = [] 

    for post in posts:
        posts_data.append({
            "id": str(post.id),
            "user_id": user.id,
            "caption": post.caption,
            "url": post.url,
            "file_type": post.file_type,
            "file_name": post.file_name,
            "created_at": post.created_at.isoformat(),
            "is_owner": post.user_id == user.id,
            "user_email": user_email
        })

    return posts_data


@instance.delete("/post/{post_id}")
async def delete_post(post_id: str, session: AsyncSession = Depends(get_session), user: User = Depends(current_active_user),):
   
    try:
        post_uuid = uuid.UUID(post_id)
        result = await session.execute(
            select(PostModel).where(PostModel.id == post_uuid)
        )
        post = result.scalar_one_or_none()

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        

        if post.user_id != user.id:
            raise HTTPException(status_code=403, detail="You do not have permission to delete this post")

        await session.delete(post)
        await session.commit()

        return {"detail": "Post deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete post: {str(e)}")
        


    
