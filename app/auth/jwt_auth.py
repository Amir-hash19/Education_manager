from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status, Depends
from jwt import InvalidSignatureError, DecodeError
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from sqlalchemy.future import select
from app.config import settings
import jwt

#import user model for verify 
from app.users.models import UserModel

security = HTTPBearer()




def generate_access_token(user_id: int, expires_in: int = 60*5) -> str:

    """this function will create an access token base on user information"""

    now = datetime.now(timezone.utc)
    payload = {
        "user_id":user_id,
        "iat":int(now.timestamp()),
        "exp":int((now + timedelta(seconds=expires_in)).timestamp()),
        "type":"access"
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")




def generate_refresh_token(user_id: int, expires_in: int = 3600*24) -> str:

    """this function will create an refresh token base on user information"""

    now = datetime.now(timezone.utc)
    payload = {
        "user_id": user_id,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=expires_in)).timestamp()),
        "type": "refresh"
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")






def decode_refresh_token(token):
    """for decoding refresh token in order to verify user"""
    try:
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        user_id = decoded.get("user_id",None)
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Authentication failed, user_id not in the payload")
        
        if decoded.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Authentication failed,token type not valid")
        
        if datetime.now(timezone.utc) > datetime.fromtimestamp(decoded["exp"], tz=timezone.utc):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Authentication failed, token expired")
        
        return user_id
        

    except InvalidSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Authentication failed, invalid signature")
    except DecodeError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Authenication failed, decode failed")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=f"Authentication failed, {e}")     








async def get_authenticated_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: AsyncSession = Depends(get_db)
    ):
    token = credentials.credentials
    try:
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        if decoded.get("type") != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

        if datetime.now(timezone.utc) > datetime.fromtimestamp(decoded["exp"], tz=timezone.utc):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")

        user_id = decoded.get("user_id")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing user_id in token")

        result = await db.execute(select(UserModel).filter_by(id=user_id))
        user_obj = result.scalar_one_or_none()
        if not user_obj:
            raise HTTPException(status_code=401, detail="User not found")

        return user_obj

    except (InvalidSignatureError, DecodeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
