from fastapi import Depends, HTTPException, status
from app.users.models import UserModel
from app.auth.jwt_auth import get_authenticated_user



async def get_current_admin(current_user: UserModel = Depends(get_authenticated_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user
