from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import datetime
from database import Base

class Employee(Base):
    __tablename__ = "employees"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    encoding = Column(String, nullable=False)

    logs = relationship("AccessLog", back_populates="employee")

class AccessLog(Base):
    __tablename__ = "access_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String, ForeignKey("employees.id"), nullable=False)
    event = Column(String, nullable=False)
    ts = Column(DateTime, default=datetime.datetime.utcnow)

    employee = relationship("Employee", back_populates="logs")
