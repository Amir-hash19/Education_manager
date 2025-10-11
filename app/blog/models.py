from sqlalchemy import Column, Integer, Boolean,Text, String, Numeric,ForeignKey, Table, DateTime, Enum, Date
from passlib.context import CryptContext
from sqlalchemy.orm import relationship
from db.database import Base
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from datetime import datetime




class StatusBlog(PyEnum):
    draft = "draft"
    published = "published"



class BlogModel(Base):
    __tablename__ = "blogs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), unique=True)
    content = Column(Text, nullable=False)
    status = Column(Enum(StatusBlog), nullable=False, default=StatusBlog.draft)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    last_update = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    
    def __repr__(self):
        return f"blog ID {self.id} and created_at{self.date_created}"




