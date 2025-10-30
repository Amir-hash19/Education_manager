from fastapi import status, HTTPException, Path, Request,Depends, APIRouter, Query
from fastapi.responses import JSONResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy import and_
from sqlalchemy.orm import selectinload
from app.bootcamp.models import BootCampCategoryModel, BootCampModel, BootCampStatus
from app.db.database import get_db
from app.users.permissions import get_current_admin 
from fastapi_cache.decorator import cache
from app.auth.jwt_auth import get_authenticated_user
from app.bootcamp.schemas import BootcampCategorySchema
from app.users.models import UserModel
from datetime import datetime, timezone
from typing import Optional

from app.bootcamp.schemas import(BootCampResponseSchema, BootcampSchema,
BootCampDeleteResponse, BootCampUpdateSchema)

router = APIRouter(prefix="/api/v1")



@router.post("/bootcamp-category")
async def create_bootcamp_category(request: Request, 
    bootcamp_category: BootcampCategorySchema,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin)
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




@router.post("/bootcamps/create", response_model=BootCampResponseSchema)
async def create_bootcamp(
    bootcamp: BootcampSchema,
    db: AsyncSession = Depends(get_db)
):
    # ---- Handle category ----
    category = None
    if bootcamp.category is not None and str(bootcamp.category).strip():
        result = await db.execute(
            select(BootCampCategoryModel).filter_by(id=bootcamp.category)
        )
        category = result.scalars().first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

    # ---- Handle instructors ----
    instructors = []
    valid_instructor_ids = [int(i) for i in bootcamp.instructors if str(i).strip().isdigit()]
    if valid_instructor_ids:
        result = await db.execute(
            select(UserModel).filter(UserModel.id.in_(valid_instructor_ids))
        )
        instructors = result.scalars().all()
        if len(instructors) != len(valid_instructor_ids):
            raise HTTPException(status_code=404, detail="One or more instructors not found")

    # ---- Create BootCamp ----
    new_bootcamp = BootCampModel(
        title=bootcamp.title,
        price=float(bootcamp.price),
        is_online=bootcamp.is_online,
        capacity=bootcamp.capacity,
        description=bootcamp.description,
        start_date=bootcamp.start_date,
        end_date=bootcamp.end_date,
        category=category,
        instructors=instructors,
        
    )

    db.add(new_bootcamp)
    await db.commit()
    await db.refresh(new_bootcamp)

    # ---- Preload relations to avoid MissingGreenlet ----
    result = await db.execute(
        select(BootCampModel)
        .options(
            selectinload(BootCampModel.instructors),
            selectinload(BootCampModel.category)
        )
        .where(BootCampModel.id == new_bootcamp.id)
    )
    bootcamp_with_relations = result.scalars().first()

    # ---- Prepare response ----
    return BootCampResponseSchema(
        id=bootcamp_with_relations.id,
        title=bootcamp_with_relations.title,
        description=bootcamp_with_relations.description or "",
        price=bootcamp_with_relations.price,
        capacity=bootcamp_with_relations.capacity,
        status=bootcamp_with_relations.status,
        is_online=bootcamp_with_relations.is_online,
        start_date=bootcamp_with_relations.start_date,
        end_date=bootcamp_with_relations.end_date,
        created_at=bootcamp_with_relations.created_at,
        updated_date=bootcamp_with_relations.updated_date,
        category=BootcampCategorySchema(
            id=bootcamp_with_relations.category.id,
            name=bootcamp_with_relations.category.name,
            date_created=bootcamp_with_relations.category.date_created
        ) if bootcamp_with_relations.category else None,
        instructors=[inst.full_name for inst in bootcamp_with_relations.instructors] if bootcamp_with_relations.instructors else []
    )



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

    
                               


@router.put("/bootcamps/{bootcamp_id}/edit", response_model=dict)
async def update_bootcamp(
    bootcamp_id: int = Path(..., title="ID of the bootcamp to update"),
    bootcamp_data: BootCampUpdateSchema = ...,
    db: AsyncSession = Depends(get_db)
):
   
    result = await db.execute(select(BootCampModel).filter(BootCampModel.id == bootcamp_id))
    bootcamp = result.scalars().first()
    
    if not bootcamp:
        raise HTTPException(status_code=404, detail="Bootcamp not found")


    for key, value in bootcamp_data.dict(exclude_unset=True).items():
        setattr(bootcamp, key, value)

    db.commit()
    db.refresh(bootcamp)

    return {"message": "Bootcamp updated successfully", "bootcamp_id": bootcamp.id}

   


    



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
    """this api is available for any user in order to check bootcamps"""
    result = await db.execute(select(BootCampModel).where(
        and_(BootCampModel.id == bootcamp_id,
            BootCampModel.status != "draft")
    ))
    bootcamp = result.scalar_one_or_none()

    if not bootcamp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bootcamp not found")

    return {"data": bootcamp}





@router.get("/bootcamps/all/list", status_code=status.HTTP_200_OK)
async def list_bootcamps(
    db: AsyncSession = Depends(get_db),
    
):
    """any user have access to this end point to check bootcamps"""
    
    query = select(BootCampModel).where(BootCampModel.status != BootCampStatus.draft)
    result = await db.execute(query)
    bootcamps = result.scalars().all()

    return {"count": len(bootcamps), "data": bootcamps}




