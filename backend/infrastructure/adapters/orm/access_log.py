from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from infrastructure.adapters.database import Base
import datetime

class AccessLog(Base):
    __tablename__ = "access_logs"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey("employees.id"))
    event = Column(String)
    ts = Column(DateTime, default=datetime.datetime.utcnow)

    employee = relationship("Employee")
