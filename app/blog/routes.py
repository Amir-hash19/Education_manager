from fastapi import status, HTTPException, Request, Depends, APIRouter, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.users.models import UserModel
from app.db.database import get_db
from app.users.permisions import get_current_admin 
from fastapi_cache.decorator import cache
from sqlalchemy import and_
from app.blog.schemas import BlogStatusEnum, BlogBaseSchema, BlogResponseSchema, BlogDeleteResponse, BlogUpdateRequest, BlogUpdateResponse
from app.users.permisions import get_current_admin

from app.blog.models import BlogModel, StatusBlog

from typing import Optional

router = APIRouter(prefix="/api/v1")




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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=str(e))
    



@router.get("/blogs", status_code=status.HTTP_200_OK)
async def list_blog(db: AsyncSession = Depends(get_db), current_admin = Depends(get_current_admin),
status_filter: Optional[str] = Query(None, description="filter blogs in published status")):
    query = select(BlogModel)

    if status_filter:
        query = query.where(BlogModel.status == status_filter)


    result = await db.execute(query)
    blogs = result.scalars().all()

    return {"count":len(blogs), "data":blogs}    






@router.get("/blogs/{blog_id}",status_code=status.HTTP_200_OK)
async def retrieve_blog(blog_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BlogModel).where(BlogModel.id == blog_id, BlogModel.status == StatusBlog.published))
    blog_obj = result.scalar_one_or_none()

    if not blog_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="blog not found")
    
    return {"data":blog_obj}





@router.delete(
    "blog/{blog_id}/edit",
    response_model=BlogDeleteResponse,
    
)
async def delete_blog(blog_id: int, db:AsyncSession = Depends(get_db),current_admin = Depends(get_current_admin)):
    result = await db.execute(
        select(BlogModel).where(BlogModel.id == blog_id)
    )
    blog_obj = result.scalar_one_or_none()

    if not blog_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"blog with ID {blog_id} not found"
        )


    await db.delete(blog_obj)
    await db.commit()

    return {"message":f"blog with ID {blog_id} deleted successfully", "status_code":status.HTTP_200_OK}







@router.put(
    "blog/{blog_id}/edit",
    response_model=BlogUpdateResponse,
    status_code=status.HTTP_200_OK,

)
async def update_blog(blog_id: int, blog:BlogUpdateRequest, db:AsyncSession = Depends(get_db),current_admin = Depends(get_current_admin)):
    result = await db.execute(
        select(BlogModel).where(BlogModel.id == blog_id)
    )
    blog_obj = result.scalar_one_or_none()

    if not blog_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blog with ID {blog_id} not found"
        )
    
    for key, value in blog.model_dump(exclude_unset=True).items():
        setattr(blog_obj, key, value)


    await db.commit()
    await db.refresh(blog_obj)

    return {
        "message":f"blog with ID {blog_id} updated successfully",
        "status_code":status.HTTP_200_OK,
        "data":blog_obj
    }    



