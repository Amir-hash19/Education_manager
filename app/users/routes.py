from app.auth.jwt_auth import(generate_access_token,
generate_refresh_token, get_authenticated_user, decode_refresh_token)

from fastapi import status, HTTPException, Path, Request,Depends, APIRouter
from fastapi.responses import JSONResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.future import select
from app.users.models import UserModel

from app.db.database import get_db
from .schemas import UserBaseSchema, UserCreateSchema, UserLoginSchema, UserUpdateSchema, UserRoleResponse, UserRetrieveSchema, AdminCreateSchema


from app.users.permisions import get_current_admin 
from fastapi_cache.decorator import cache


# from app.main import limiter
router = APIRouter(prefix="/api/v1")



@router.post("/user", response_model=UserBaseSchema)
async def create_user(request: Request, user: UserCreateSchema, db: AsyncSession = Depends(get_db)):
    try:
        # بررسی وجود کاربر
        result = await db.execute(select(UserModel).filter_by(email=user.email.lower()))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # ایجاد کاربر جدید
        user_obj = UserModel(
            email=user.email.lower(),
            full_name=user.full_name,
            national_id=user.national_id,
            gender=user.gender
        )
        user_obj.set_password(user.password)
        db.add(user_obj)
        await db.commit()
        await db.refresh(user_obj)

        # تولید توکن‌ها
        access_token = generate_access_token(user_obj.id)
        refresh_token = generate_refresh_token(user_obj.id)

        return JSONResponse(
            content={
                "detail": "User created successfully",
                "access": str(access_token),
                "refresh": str(refresh_token)
            },
            status_code=status.HTTP_201_CREATED
        )

    # خطاهای مربوط به دیتابیس (مثل اتصال یا constraint)
    except IntegrityError as ie:
        await db.rollback()
        print("IntegrityError:", str(ie))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error: " + str(ie.orig)
        )
    except SQLAlchemyError as se:
        await db.rollback()
        print("SQLAlchemyError:", str(se))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error: " + str(se)
        )

    # خطاهای عمومی دیگر
    except Exception as e:
        await db.rollback()
        print("OtherError:", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )



                         
                         
@router.post("/login", status_code=status.HTTP_202_ACCEPTED)
async def user_login(request: UserLoginSchema,
    response:Response,
    db:AsyncSession = Depends(get_db)) -> dict:

    result = await db.execute(select(UserModel).filter_by(email=request.email.lower()))
    user = result.scalar_one_or_none()

    if not user or not user.verify_password(request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    
    access_token = generate_access_token(user.id) 
    refresh_token = generate_refresh_token(user.id) 
    


    return JSONResponse(
        content={
            "detail": "Login successful",
            "access_token": str(access_token),
            "refresh_token": str(refresh_token),
            "token_type": "bearer"
        }
    )

    

    

@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh(request: Request, response: Response, db:AsyncSession = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token")
    try:
        payload = decode_refresh_token(refresh_token) 
        user_id = payload.get("sub")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )    
    user = await db.execute(select(UserModel).filter(UserModel.id == int(user_id)))
    user = user.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    new_access = generate_access_token({"sub": str(user.id)})
    

    return {
        "detail":"Tokens refreshed successfully",
        "access_token":new_access,
        "token_type": "bearer"
    }




@router.get("/user/me", response_model=UserRetrieveSchema)
@cache(expire=300)
async def user_retrieve(current_user: UserModel = Depends(get_authenticated_user)):
    return current_user





@router.put("/user/me", response_model=UserBaseSchema)
async def update_current_user(
    request: UserUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_authenticated_user)
):
    try:
        update_data = request.model_dump(exclude_unset=True)

        if "password" in update_data:
            update_data["password"] = UserModel.hash_password(update_data["password"])

        for key, value in update_data.items():
            setattr(current_user, key, value)

        db.add(current_user)
        await db.commit()
        await db.refresh(current_user)

        return current_user
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user: {str(e)}"
        )    
                    




@router.delete("/user/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_authenticated_user)
):

    try:
        await db.delete(current_user)
        await db.commit()
        return {
            "detail":"Your account deleted successfully",
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user: {str(e)}"
        )
    



@router.put("/admin/users/{user_id}/role", response_model=UserRoleResponse)
async def update_user_role(
    user_id: int,
    request: UserRoleResponse,
    db: AsyncSession = Depends(get_db),
    admin_user: UserModel = Depends(get_current_admin)
):
    try:
        result = await db.execute(select(UserModel).filter_by(id=user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.role = request.role
        db.add(user)
        await db.commit()
        await db.refresh(user)

        return user
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating role: {str(e)}"
        )





@router.post("/admin", response_model=AdminCreateSchema)
async def create_user(request: Request, user: AdminCreateSchema, owner_id: int, db: AsyncSession = Depends(get_db)):
    try:
        # بررسی وجود کاربر
        result = await db.execute(select(UserModel).filter_by(email=user.email.lower()))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            # بررسی roles یا گروه‌های کاربر
            if set(user.roles).intersection(set(existing_user.roles)):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User already exists in one of the specified roles/groups"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User with this email already exists"
                )
        
       
        user_obj = UserModel(
            email=user.email.lower(),
            full_name=user.full_name,
            national_id=user.national_id,
            gender=user.gender,
            roles=user.roles,
            owner_id=owner_id 
        )
        user_obj.set_password(user.password)
        db.add(user_obj)
        await db.commit()
        await db.refresh(user_obj)

        # تولید توکن‌ها
        access_token = generate_access_token(user_obj.id)
        refresh_token = generate_refresh_token(user_obj.id)

        return JSONResponse(
            content={
                "detail": "User created successfully",
                "access": str(access_token),
                "refresh": str(refresh_token)
            },
            status_code=status.HTTP_201_CREATED
        )
    except IntegrityError as ie:
        await db.rollback()
        print("IntegrityError:", str(ie))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error: " + str(ie.orig)
        )
    except SQLAlchemyError as se:
        await db.rollback()
        print("SQLAlchemyError:", str(se))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error: " + str(se)
        )
    except Exception as e:
        await db.rollback()
        print("OtherError:", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )
