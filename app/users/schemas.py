from pydantic import BaseModel, EmailStr, Field, field_validator, constr
from typing import List, Optional, Literal
from datetime import datetime
from enum import Enum



class GenderEnum(str, Enum):
    male = "male"
    female = "female"




class UserBaseSchema(BaseModel):
    full_name: str = Field(..., max_length=200)
    national_id : str = Field(...,pattern=r"^\d{10}$")
    email: EmailStr
    create_at: datetime
    gender: Literal["male", "female"]





class UserCreateSchema(UserBaseSchema):
    password: str = Field(...,max_length=70, min_length=8)
    password_confirm: str = Field(...,max_length=70,min_length=8,
    description="password confirmation")
    
    @field_validator("password_confirm")
    def check_passwords_match(cls, password_confirm, validation):
        if not (password_confirm == validation.data.get("password")):
            raise ValueError("passwords invalid")
        return password_confirm





class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(...,max_length=70, min_length=8)



class UserUpdateSchema(UserBaseSchema):
    password: str 
    updated_date : datetime



class UserRoleResponse(BaseModel):
    updated_date : datetime
    role: str
