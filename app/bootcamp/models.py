from sqlalchemy import Column, Integer, Boolean,Text, String, Numeric,ForeignKey, Table, DateTime, Enum, Date
from passlib.context import CryptContext
from sqlalchemy.orm import relationship
from app.db.database import Base
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from datetime import datetime




class BootCampCategoryModel(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    bootcamp_list = relationship("BootCampModel", back_populates="category")



    def __repr__(self):
        return f"bootcamp Category ID {self.id} and created_at{self.date_created}"


bootcamp_instructors = Table(
    "bootcamp_instructors",
    Base.metadata,
    Column("bootcamp_id", Integer, ForeignKey("bootcamps.id", ondelete="CASCADE"), primary_key=True),
    Column("instructor_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
)



class BootCampStatus(PyEnum):
    draft = "draft"
    available = "available"
    finished = "finished"
    canceled = "canceled"


class BootCampModel(Base):
    __tablename__ = "bootcamps"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(Enum(BootCampStatus), nullable=False, default=BootCampStatus.draft)


    instructors = relationship(
        "UserModel",
        secondary=bootcamp_instructors,
        back_populates="bootcamps"
    )


    title = Column(String(200), unique=True)
    price = Column(Numeric(10, 2), nullable=False, default=0.00)
    is_online = Column(Boolean, default=True, nullable=False)
    capacity = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_date = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"bootcamp  ID {self.id} and created_at{self.created_at}"

















