from fastapi import status, HTTPException, Path, Request,Depends, APIRouter, Query
from fastapi.responses import JSONResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy import and_
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



    


@router.post(
    "/bootcamp",response_model=BootCampResponseSchema
)
async def create_bootcamp(data: BootcampSchema,db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin)):
    category_obj = None
    if data.category:
        result = await db.execute(select(BootCampCategoryModel).where(BootCampCategoryModel.name == data.category))
        category_obj = result.scalar_one_or_none()
        if not category_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Category '{data.category}' not found")
        
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

    if data.instructors:
        for name in data.instructors:
            result = await db.execute(select(UserModel).where(UserModel.full_name == name))
            instructor = result.scalar_one_or_none()
            if not instructor:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Instructor '{name}' not found.")
            bootcamp.instructors.append(instructor)    
    db.add(bootcamp)
    await db.commit()
    await db.refresh(bootcamp)

    bootcamp_data = BootCampResponseSchema.model_validate(bootcamp)

    return {
        "status_code":status.HTTP_201_CREATED,
        "message":"Bootcamp created successfully",
        "data":bootcamp_data
    }




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

    
                               


@router.put("bootcamp/{bootcamp_id}", status_code=status.HTTP_200_OK)
async def update_bootcamp(bootcamp_id: int, bootcamp_data: BootcampUpdateSchema,
    db: AsyncSession = Depends(get_db), current_user = Depends(get_current_admin)):

    result = await db.execute(select(BootCampModel).where(BootCampModel.id==bootcamp_id))
    bootcamp = result.scalar_one_or_none()
    if not bootcamp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="object not found")
    
    update_data = bootcamp.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(bootcamp, key, value)

    await db.commit()
    await db.refresh(bootcamp)

    return {"message": "Bootcamp updated successfully", "data": bootcamp}    


    



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