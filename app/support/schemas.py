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






class TicketMessageBaseSchema(BaseModel):
    user_phone: str
    message_status: MessageStatus = Field(default=MessageStatus.pending)
    message: str
    date_created: datetime = Field(default_factory=datetime.now)



class TicketMessageResponseSchema(TicketBabseSchema):
    id : int




class TicketMessageUpdateSchema(BaseModel):
    message_status: Optional[MessageStatus]
    admin_response: Optional[str]
    