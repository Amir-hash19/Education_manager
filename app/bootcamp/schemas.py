from pydantic import BaseModel, EmailStr, Field, field_validator, constr
from typing import List, Optional, Literal
from decimal import Decimal
from datetime import datetime
from datetime import date
from enum import Enum



class BootCampStatus(str, Enum):
    draft = "draft"
    available = "available"
    finished = "finished"
    canceled = "canceled"


class BootcampCategorySchema(BaseModel):
    name: str = Field(..., max_length=150)
    date_created: datetime





class BootCampOut(BaseModel):
    id: int
    instructors: Optional[List[str]] = None  
    class Config:
        orm_mode = True



class BootcampSchema(BaseModel):
    title: str =Field(...,max_length=200)
    description: str = Field(...,description="bootcamp info")
    price: Decimal = Field(...,ge=0, description="price of bootcamp")
    capacity: int = Field(...,ge=0, description="capacity of bootcamp")
    status: BootCampStatus = Field(default=BootCampStatus.draft)
    is_online: bool = Field(default=False, description="check the onlien or offline boot camp")
    start_date: datetime = Field(...,description="Booking start date and time")
    end_date: datetime = Field(..., description="Booking end date and time (user-defined)")
    instructors: Optional[List[str]] = Field(None, description="List of instructor names")
    category: Optional[str] = Field(None, description="category name")







class BootCampResponseSchema(BaseModel):
    id: int
    title: str
    description: str
    price: Decimal
    capacity: int
    status: BootCampStatus
    is_online: bool
    start_date: datetime
    end_date: datetime
    created_at: datetime
    updated_date: datetime
    category: Optional[BootcampCategorySchema] = None  
    instructors: Optional[List[str]] = None



class BootCampDeleteResponse(BaseModel):
    status_code: int
    message: str




class BootCampUpdateSchema(BaseModel):
    title: Optional[str]
    price: Optional[Decimal]
    is_online: Optional[bool]
    capacity: Optional[int]
    description: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    status: Optional[BootCampStatus]
    category_id: Optional[int]

    class Config:
        orm_mode = True

