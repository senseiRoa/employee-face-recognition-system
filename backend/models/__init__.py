from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
import datetime
from database import Base


class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    username = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    warehouses = relationship(
        "Warehouse", back_populates="company", cascade="all, delete-orphan"
    )
    users = relationship("User", back_populates="company", cascade="all, delete-orphan")
    login_logs = relationship("LoginLog", back_populates="company")


class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String(255))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    users = relationship("User", back_populates="role")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    username = Column(String(100), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    email = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    company = relationship("Company", back_populates="users")
    role = relationship("Role", back_populates="users")
    login_logs = relationship("UserLoginLog", back_populates="user")


class Warehouse(Base):
    __tablename__ = "warehouses"
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    name = Column(String(100), nullable=False)
    location = Column(String(255))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    company = relationship("Company", back_populates="warehouses")
    tablets = relationship(
        "Tablet", back_populates="warehouse", cascade="all, delete-orphan"
    )
    employees = relationship("Employee", back_populates="warehouse")


class Tablet(Base):
    __tablename__ = "tablets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    name = Column(String(100), nullable=False)
    jwt_token = Column(Text)
    last_sync = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    warehouse = relationship("Warehouse", back_populates="tablets")


class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, autoincrement=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(100))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    warehouse = relationship("Warehouse", back_populates="employees")
    encodings = relationship(
        "FaceEncoding", back_populates="employee", cascade="all, delete-orphan"
    )
    logs = relationship("AccessLog", back_populates="employee")


class FaceEncoding(Base):
    __tablename__ = "face_encodings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    encoding = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    employee = relationship("Employee", back_populates="encodings")


class AccessLog(Base):
    __tablename__ = "access_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"))
    event = Column(String(100), nullable=False)
    ts = Column(DateTime, default=datetime.datetime.utcnow)

    employee = relationship("Employee", back_populates="logs")
    warehouse = relationship("Warehouse")


class LoginLog(Base):
    __tablename__ = "login_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    location = Column(String(100))
    browser = Column(String(100))

    company = relationship("Company", back_populates="login_logs")


class UserLoginLog(Base):
    __tablename__ = "user_login_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    location = Column(String(100))
    browser = Column(String(100))

    user = relationship("User", back_populates="login_logs")
