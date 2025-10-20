from fastapi import status, HTTPException, Request, Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.users.models import UserModel
from app.db.database import get_db
from app.users.permisions import get_current_admin 
from fastapi_cache.decorator import cache

from app.blog.schemas import BlogStatusEnum, BlogBaseSchema, BlogResponseSchema
from app.users.permisions import get_current_admin

from app.blog.models import BlogModel, StatusBlog
router = APIRouter(prefix="/api/v1")



import traceback
@router.post("/blog/create", response_model=BlogResponseSchema)
async def create_blog(request:Request, blog: BlogBaseSchema, db: AsyncSession = Depends(get_db),
                       current_admin = Depends(get_current_admin)):
    try:
        blog_obj = BlogModel(
            title=blog.title,
            content=blog.content,
            status=blog.status
        )

        db.add(blog_obj)
        await db.commit()
        await db.refresh(blog_obj)
        return blog_obj    
    except Exception as e:
        await db.rollback()
        print("❌ ERROR:", traceback.format_exc()) 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=str(e))
    