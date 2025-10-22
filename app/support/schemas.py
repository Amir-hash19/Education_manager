from pydantic import BaseModel, EmailStr, Field, field_validator, constr
from typing import List, Optional, Literal
from decimal import Decimal
from datetime import datetime
from datetime import date
from enum import Enum




class MessageStatus(str, Enum):
    pending = "pending"
    answered = "answered"
    notanswered = "notanswered"
    closed = "closed"




class TicketBabseSchema(BaseModel):
    title: str = Field(..., max_length=100)
    description: str = Field(...,description="Message content")
    created_at: datetime = Field(default_factory=datetime.now)



class TicketResponseSchema(TicketBabseSchema):
    id: int