from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Optional
from datetime import datetime
from enum import Enum



class GenderEnum(str, Enum):
    male = "male"
    female = "female"




class UserBaseSchema(BaseModel):
    full_name: str = Field(..., max_length=200)
    national_id : int = Field(...,max_length=10,min_length=0)
    email: EmailStr
    gender: GenderEnum = GenderEnum.male




class UserCreateSchema(UserBaseSchema):
    password: str = Field(max_length=70, min_length=8)
    password_confirm: str = Field(max_length=70,min_length=8,
    description="password confirmation")