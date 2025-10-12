from sqlalchemy import(
        Column, Integer,Text, 
        func, String, ForeignKey,
        Table, DateTime, Enum)

from sqlalchemy.orm import relationship
from app.db.database import Base
from enum import Enum as PyEnum
from datetime import datetime






class TicketModel(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"title <{self.title} and date_created {self.created_at}>"




class MessageStatusEnum(PyEnum):
    pending = "pending"
    answered = "answered"
    notanswered = "notanswered"
    closed = "closed"


class TicketMessageModel(Base):
    __tablename__ = "ticket_messages"

    id = Column(Integer, primary_key=True, index=True)

    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=True)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)

    user_phone = Column(String(20), unique=True, nullable=True)
    message_status = Column(Enum(MessageStatusEnum), default=MessageStatusEnum.pending)
    message = Column(Text, nullable=True)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    attachment = Column(String(255), nullable=True)
    slug = Column(String(255), unique=True, nullable=False)
    title = Column(String(50), nullable=True)

    admin_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    admin_response = Column(Text, nullable=True)

    def __repr__(self):
        return f"title <{self.title} and date_created {self.date_created}>"










