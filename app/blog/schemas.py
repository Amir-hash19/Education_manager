from pydantic import BaseModel, EmailStr, Field, field_validator, constr
from typing import List, Optional, Literal
from datetime import datetime
from enum import Enum as PyEnum



class BlogStatusEnum(str ,PyEnum):
    draft = "draft"
    published = "published"




class BlogBaseSchema(BaseModel):
    title : str = Field(...,max_length=150)
    content : str = Field(...,description="main content for blog")
    status: Optional[str] = "draft"
    date_created: datetime
    last_update: datetime

    class Config:
        from_attributes = True


class BlogResponseSchema(BlogBaseSchema):
    id : int



class BlogDeleteResponse(BaseModel):
    status_code: int
    message: str




class BlogUpdateRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[BlogStatusEnum] = None  

    model_config = {"from_attributes": True}



class BlogUpdateResponse(BaseModel):
    message: str
    status_code: int
    data: BlogUpdateRequest

    