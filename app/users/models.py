from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, Enum
from app.bootcamp.models import BootCampModel, bootcamp_instructors
from passlib.context import CryptContext
from sqlalchemy.orm import relationship
from app.db.database import Base
from enum import Enum as PyEnum
from datetime import datetime

pwd_context = CryptContext(schemes=["argon2"],deprecated="auto")



class RoleEnum(PyEnum):
    admin = "admin"
    instructor = "instructor"
    student = "student"





class GenderEnum(PyEnum):
    male = "male"
    female = "female"




class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(200))
    password = Column(String)
    email = Column(String(200), unique=True, index=True)
    role = Column(Enum(RoleEnum, name="roleenum"), nullable=False, default=RoleEnum.student)
    national_id = Column(String(10),nullable=False)
    gender = Column(Enum(GenderEnum), nullable=False, default=GenderEnum.male)
    created_at = Column(DateTime, default=datetime.now)
    updated_date = Column(DateTime(),default=datetime.now,onupdate=datetime.now) 



    bootcamp = relationship(
        "BootCampModel",
        secondary="bootcamp_instructors",
        back_populates="instructors"
    )
    

    @classmethod
    def hash_password(self, plain_password: str) -> str:
        return pwd_context.hash(plain_password)
    
    def verify_password(self, plain_password: str) -> bool:
        return pwd_context.verify(plain_password, self.password)
    
    def set_password(self, plain_password: str) -> None:
        self.password = self.hash_password(plain_password) 
        

    def __repr__(self):
        return f"email is {self.email} and full name is {self.full_name}"
