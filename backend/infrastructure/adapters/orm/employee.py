from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from infrastructure.adapters.database import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)

    encodings = relationship("FaceEncoding", back_populates="employee")

class FaceEncoding(Base):
    __tablename__ = "face_encodings"

    id = Column(Integer, primary_key=True, index=True)
    encoding = Column(String)
    employee_id = Column(String, ForeignKey("employees.id"))

    employee = relationship("Employee", back_populates="encodings")
