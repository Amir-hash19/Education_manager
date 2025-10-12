from app.auth.jwt_auth import(generate_access_token,
generate_refresh_token, get_authenticated_user)

from fastapi import status, HTTPException, Path, Request,Depends, APIRouter
from fastapi.responses import JSONResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.users.models import UserModel, RoleModel

from app.db.database import get_db
from .schemas import UserBaseSchema, UserCreateSchema

from slowapi import Limiter
from slowapi.util import get_remote_address

# from app.main import limiter

userrouter = APIRouter(prefix="/api/v1")



@userrouter.post("/user", response_model=UserBaseSchema)
@Limiter(key_func=get_remote_address).limit("5/minute")
async def create_user(request:Request, user: UserCreateSchema, db:AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(UserModel).filter_by(email=user.email.lower()))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user with this email already exists"
            )
        
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

        access_token = generate_access_token(user_obj.id)
        refresh_token = generate_refresh_token(user_obj.id)

        return JSONResponse(
            content={
                "detail": "user created successfully",
                "access": access_token,
                "refresh": refresh_token
            },
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )



                         
                         

    


    

    
