from pydantic import BaseModel, EmailStr, Field, field_validator, constr
from typing import List, Optional, Literal
from datetime import datetime
from enum import Enum




class BootcampCategorySchema(BaseModel):
    name: str = Field(..., max_length=150)
    date_created: datetime



