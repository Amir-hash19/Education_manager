from fastapi import status, HTTPException, Path, Request,Depends, APIRouter
from fastapi.responses import JSONResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.future import select
from app.bootcamp.models import BootCampCategoryModel, BootCampModel
from app.db.database import get_db
from app.users.permisions import get_current_admin 
from fastapi_cache.decorator import cache
from app.auth.jwt_auth import get_authenticated_user
from app.bootcamp.schemas import BootcampCategorySchema
from app.users.models import UserModel
from datetime import datetime, timezone
router = APIRouter(prefix="/api/v1")





@router.post("/bootcamp-category")
async def create_bootcamp_category(request: Request, 
    bootcamp_category: BootcampCategorySchema,
    db: AsyncSession = Depends(get_db),
    admin_user:  UserModel=Depends(get_current_admin)):
    try:
        bootcamp_category_obj = BootCampCategoryModel(
            name=bootcamp_category.name,
            date_created=datetime.now(timezone.utc)
        )
        db.add(bootcamp_category_obj)
        await db.commit()
        await db.refresh(bootcamp_category_obj)

        return JSONResponse(content={
            "message":"bootcamp category definded successfully",
            "bootcamp ID":bootcamp_category_obj.id
        }, status_code=status.HTTP_201_CREATED)

    except IntegrityError as ie:
        await db.rollback()
        print("IntegrityError:", str(ie))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error: " + str(ie.orig)
        ) 




@router.delete(
    "/bootcamp-category/{bootcamp_category_id}/delete",
    status_code=status.HTTP_200_OK
)
async def delete_bootcamp_category(
    bootcamp_category_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin)
):
   
    result = await db.execute(
        select(BootCampCategoryModel).filter(BootCampCategoryModel.id == bootcamp_category_id)
    )
    bootcamp_category_obj = result.scalar_one_or_none()

    if not bootcamp_category_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bootcamp category with id {bootcamp_category_id} does not exist"
        )

    await db.delete(bootcamp_category_obj)
    await db.commit()

    return JSONResponse(
        content={"detail": "Selected bootcamp category deleted successfully"},
        status_code=status.HTTP_200_OK
    )      



    
