from fastapi import status, HTTPException, Path, Request,Depends, APIRouter, Query
from fastapi.responses import JSONResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy import and_
from sqlalchemy.orm import selectinload
from app.bootcamp.models import BootCampCategoryModel, BootCampModel
from app.db.database import get_db
from app.users.permisions import get_current_admin 
from fastapi_cache.decorator import cache
from app.auth.jwt_auth import get_authenticated_user
from app.bootcamp.schemas import BootcampCategorySchema
from app.users.models import UserModel
from datetime import datetime, timezone
from typing import Optional

from app.bootcamp.schemas import(BootCampResponseSchema, BootcampSchema,
BootCampDeleteResponse, BootcampUpdateSchema)

router = APIRouter(prefix="/api/v1")



@router.post("/bootcamp-category")
async def create_bootcamp_category(request: Request, 
    bootcamp_category: BootcampCategorySchema,
    db: AsyncSession = Depends(get_db),
   ):
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



@router.post("/bootcamp", response_model=BootCampResponseSchema)
async def create_bootcamp(
    data: BootcampSchema,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin)
):
    try:
        existing = await db.execute(select(BootCampModel).where(BootCampModel.title == data.title))
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Bootcamp with title '{data.title}' already exists."
            )

    
        category_obj = None
        if data.category:
            result = await db.execute(
                select(BootCampCategoryModel).where(BootCampCategoryModel.name == data.category)
            )
            category_obj = result.scalar_one_or_none()
            if not category_obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Category '{data.category}' not found"
                )

    
        bootcamp = BootCampModel(
            title=data.title,
            description=data.description,
            price=data.price,
            capacity=data.capacity,
            is_online=data.is_online,
            start_date=data.start_date,
            end_date=data.end_date,
            category_id=category_obj.id if category_obj else None,
        )

        # 4️⃣ اضافه کردن instructors
        if data.instructors:
            for email in data.instructors:
                result = await db.execute(
                    select(UserModel).where(UserModel.email == email)
                )
                instructor = result.scalar_one_or_none()
                if not instructor:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Instructor '{email}' not found."
                    )
                bootcamp.instructors.append(instructor)

        # 5️⃣ ذخیره در دیتابیس
        db.add(bootcamp)
        await db.commit()
        await db.refresh(bootcamp)


        result = await db.execute(
            select(BootCampModel)
            .options(selectinload(BootCampModel.instructors))
            .where(BootCampModel.id == bootcamp.id)
        )
        bootcamp = result.scalar_one()

        bootcamp_data = BootCampResponseSchema.model_validate({
            "id": bootcamp.id,
            "title": bootcamp.title,
            "description": bootcamp.description,
            "price": float(bootcamp.price),
            "capacity": bootcamp.capacity,
            "status": bootcamp.status,
            "is_online": bootcamp.is_online,
            "start_date": bootcamp.start_date,
            "end_date": bootcamp.end_date,
            "created_at": bootcamp.created_at,
            "updated_date": bootcamp.updated_date,
            "category": BootcampCategorySchema.model_validate({
                "id": bootcamp.category.id,
                "name": bootcamp.category.name,
                "date_created": bootcamp.category.date_created
            }) if bootcamp.category else None,
            "instructors": [i.email for i in bootcamp.instructors]
        })
    

    
        return bootcamp_data
    
    except Exception as e:
        await db.rollback()
        raise e



@router.delete(
    "bootcamp/{bootcamp_id}",
    response_model=BootCampDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="delete a bootcamp"
)
async def delete_bootcamp(bootcamp_id: int, db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_admin
)):
    result = await db.execute(
        select(BootCampModel).where(BootCampModel.id==bootcamp_id)
    )
    bootcamp = result.scalar_one_or_none()

    if not bootcamp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bootcamp with ID {bootcamp_id} not found"
        )
    await db.delete(bootcamp)
    await db.commit()

    return {
        "status_code":int(status.HTTP_200_OK),
        "message":f"Bootcamp with ID {bootcamp_id} delete successfully"
    }

    
                               


@router.put("/bootcamp/{bootcamp_id}/update", status_code=status.HTTP_200_OK)
async def update_bootcamp(
    bootcamp_id: int, 
    bootcamp_data: BootcampUpdateSchema,
    db: AsyncSession = Depends(get_db), 
    current_user = Depends(get_current_admin)
):
    
    result = await db.execute(select(BootCampModel).where(BootCampModel.id == bootcamp_id))
    bootcamp = result.scalar_one_or_none()
    if not bootcamp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="object not found")
    
  
    update_fields = bootcamp_data.model_dump(exclude_unset=True)

    # فیلدهای ساده
    simple_fields = ["title", "description", "price", "capacity", "is_online", "status", "start_date", "end_date"]
    for key in simple_fields:
        if key in update_fields:
            setattr(bootcamp, key, update_fields[key])

        # آپدیت category
    if "category" in update_fields:
        cat_name = update_fields["category"]  # حالا str است
        result = await db.execute(
            select(BootCampCategoryModel).where(BootCampCategoryModel.name == cat_name)
        )
        category_obj = result.scalar_one_or_none()
        if not category_obj:
            raise HTTPException(status_code=404, detail=f"Category '{cat_name}' not found")
        bootcamp.category = category_obj
    
        

        if "instructors" in update_fields:
            bootcamp.instructors = []  
            for email in update_fields["instructors"]:
                result = await db.execute(select(UserModel).where(UserModel.email == email))
            instructor = result.scalar_one_or_none()
            if not instructor:
                raise HTTPException(status_code=404, detail=f"Instructor '{email}' not found")
            bootcamp.instructors.append(instructor)

    await db.commit()
    await db.refresh(bootcamp)

    return bootcamp


   


    



@router.get("/bootcamps/{bootcamp_id}", status_code=status.HTTP_200_OK)
async def retrieve_bootcamp(bootcamp_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BootCampModel).where(BootCampModel.id == bootcamp_id))
    bootcamp = result.scalar_one_or_none()

    if not bootcamp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bootcamp not found")

    return {"data": bootcamp}









@router.get("/bootcamps", status_code=status.HTTP_200_OK)
async def list_bootcamps(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_admin), 
    status_filter: Optional[str] = Query(None, description="Filter by bootcamp status, e.g. draft or available")
):
    """Only admin have access to this end point"""
    query = select(BootCampModel)

  
    if status_filter:
        query = query.where(BootCampModel.status == status_filter)

    result = await db.execute(query)
    bootcamps = result.scalars().all()

    return {"count": len(bootcamps), "data": bootcamps}





@router.get("/bootcamps/{bootcamp_id}", status_code=status.HTTP_200_OK)
async def retrieve_bootcamp(bootcamp_id: int, db: AsyncSession = Depends(get_db)):
    """this api is availabe for any user in order to check bootcamps"""
    result = await db.execute(select(BootCampModel).where(
        and_(BootCampModel.id == bootcamp_id,
            BootCampModel.status != "draft")
    ))
    bootcamp = result.scalar_one_or_none()

    if not bootcamp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bootcamp not found")

    return {"data": bootcamp}





@router.get("/bootcamps", status_code=status.HTTP_200_OK)
async def list_bootcamps(
    db: AsyncSession = Depends(get_db),
    
):
    """any user have access to this end point to check bootcamps"""
    
    query = select(BootCampModel).where(BootCampModel.status != "draft")
    result = await db.execute(query)
    bootcamps = result.scalars().all()

    return {"count": len(bootcamps), "data": bootcamps}





from app.celery_conf import add_number


@router.get("/initiate-celery-task", status_code=200)
async def start_celery_task():
    add_number.delay(1,2)
    return JSONResponse(content={"task":"Done"})
