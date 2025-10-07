from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import relationship
import datetime
from database import Base


class Company(Base):
    """Company entity - top level organization"""
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(String(255), nullable=True)
    status = Column(Boolean, default=True, nullable=False)  # True = Active, False = Inactive
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    warehouses = relationship(
        "Warehouse", back_populates="company", cascade="all, delete-orphan"
    )


class Warehouse(Base):
    """Warehouse entity - physical location for employee access control"""
    __tablename__ = "warehouses"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    name = Column(String(100), nullable=False)
    location = Column(String(255))
    timezone = Column(String(50), default="UTC")  # New field for timezone support
    is_active = Column(Boolean, default=True)     # New field for warehouse status
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="warehouses")
    users = relationship("User", back_populates="warehouse")
    employees = relationship("Employee", back_populates="warehouse")


class Role(Base):
    """Role entity with warehouse-level permissions"""
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String(255))
    
    # Warehouse-level permissions (JSON field for flexibility)
    permissions = Column(JSON, nullable=True)  # e.g., {"warehouse_access": ["read", "write"], "employee_management": ["read"]}
    
    # Scope levels: "global", "warehouse", "local"
    scope = Column(String(20), default="warehouse", nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="role")


class User(Base):
    """User entity linked to specific warehouse instead of company"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)  # Changed from company_id
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    
    username = Column(String(100), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Password management fields
    password_changed_at = Column(DateTime, nullable=True)
    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)

    # Relationships
    warehouse = relationship("Warehouse", back_populates="users")  # Changed from company
    role = relationship("Role", back_populates="users")
    user_login_logs = relationship("UserLoginLog", back_populates="user", cascade="all, delete-orphan")
    password_history = relationship("PasswordHistory", back_populates="user", cascade="all, delete-orphan")


class Employee(Base):
    """Employee entity for face recognition and access control"""
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(100))
    employee_code = Column(String(50), nullable=True, unique=True)  # New field for employee identification
    department = Column(String(100), nullable=True)               # New field
    position = Column(String(100), nullable=True)                 # New field
    is_active = Column(Boolean, default=True)                     # New field
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    warehouse = relationship("Warehouse", back_populates="employees")
    encodings = relationship("FaceEncoding", back_populates="employee", cascade="all, delete-orphan")
    access_logs = relationship("AccessLog", back_populates="employee", cascade="all, delete-orphan")


class FaceEncoding(Base):
    """Face encoding data for employees"""
    __tablename__ = "face_encodings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    encoding = Column(Text, nullable=False)
    encoding_version = Column(String(20), default="1.0")  # New field for versioning
    confidence_score = Column(String(10), nullable=True)   # New field for encoding quality
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    employee = relationship("Employee", back_populates="encodings")


class AccessLog(Base):
    """Enhanced access log with additional information (removed warehouse FK as it's implicit via employee)"""
    __tablename__ = "access_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    # Event information
    event_type = Column(String(50), nullable=False)  # "entry", "exit", "denied", "unknown"
    access_method = Column(String(50), nullable=True)  # "face_recognition", "manual", "card"
    
    # Additional context information
    confidence_score = Column(String(10), nullable=True)  # Face recognition confidence
    device_info = Column(JSON, nullable=True)            # Camera/device information
    location_details = Column(JSON, nullable=True)       # Specific location within warehouse
    additional_data = Column(JSON, nullable=True)               # Flexible field for additional data
    
    # Status and verification
    is_verified = Column(Boolean, default=False)         # Manual verification flag
    notes = Column(Text, nullable=True)                  # Human-readable notes
    
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    employee = relationship("Employee", back_populates="access_logs")


class UserLoginLog(Base):
    """Enhanced user login tracking with additional security information"""
    __tablename__ = "user_login_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Basic login information
    login_type = Column(String(50), default="password")  # "password", "token", "sso"
    status = Column(String(20), default="success")       # "success", "failed", "blocked"
    
    # Client information
    ip_address = Column(String(45), nullable=True)       # IPv6 compatible
    user_agent = Column(String(500), nullable=True)
    location = Column(String(100), nullable=True)
    browser = Column(String(100), nullable=True)
    
    # Security context
    session_id = Column(String(100), nullable=True)
    failed_attempts = Column(Integer, default=0)
    security_flags = Column(JSON, nullable=True)         # Suspicious activity flags
    
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="user_login_logs")


class PasswordHistory(Base):
    """Password history for security compliance"""
    __tablename__ = "password_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="password_history")


class RefreshToken(Base):
    """Refresh token management for secure authentication"""
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token = Column(String(255), nullable=False, unique=True, index=True)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Tracking information
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible

    # Relationships
    user = relationship("User")