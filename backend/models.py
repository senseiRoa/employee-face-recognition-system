from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import datetime
from database import Base

class Employee(Base):
    __tablename__ = "employees"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)

    encodings = relationship("FaceEncoding", back_populates="employee", cascade="all, delete-orphan")
    logs = relationship("AccessLog", back_populates="employee")


class FaceEncoding(Base):
    __tablename__ = "face_encodings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String, ForeignKey("employees.id"), nullable=False)
    encoding = Column(String, nullable=False)
    # created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    employee = relationship("Employee", back_populates="encodings")

class AccessLog(Base):
    __tablename__ = "access_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String, ForeignKey("employees.id"), nullable=False)
    event = Column(String, nullable=False)
    ts = Column(DateTime, default=datetime.datetime.utcnow)

    employee = relationship("Employee", back_populates="logs")
