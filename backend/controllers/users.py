from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr

from database import get_db
from services import user_service
from dependencies import get_current_user
from models import User
from utils.password_policy import PasswordValidator, PasswordValidationError

router = APIRouter()


# Response and request schemas
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool
    warehouse_id: int
    role_id: int
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserCreateRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    warehouse_id: Optional[int] = None
    role_id: int = 3  # Default: employee


class UserUpdateRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    warehouse_id: Optional[int] = None
    role_id: Optional[int] = None
    is_active: Optional[bool] = None


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information
    """
    return current_user


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new user with strong password validation
    Only admins and managers can create users
    Managers can only create users in their warehouse and cannot create admin users
    """
    # Validate password first
    try:
        PasswordValidator.validate_password(
            user_data.password, user_data.username, user_data.email
        )
    except PasswordValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password validation failed: {e.message}",
        )

    # Verify permissions - only admin and manager can create users
    if current_user.role.name not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create users. Only admins and managers can create new users.",
        )

    # If not admin, can only create users in their own warehouse
    target_warehouse_id = user_data.warehouse_id or current_user.warehouse_id
    if (
        current_user.role.name != "admin"
        and target_warehouse_id != current_user.warehouse_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Managers can only create users in their own warehouse",
        )

    # Verify that role_id is valid according to current user permissions
    if current_user.role.name == "manager" and user_data.role_id == 1:  # admin role
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Managers cannot create admin users",
        )

    # Check if username already exists
    existing_user = user_service.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Check if email already exists
    existing_email = user_service.get_user_by_email(db, user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    try:
        new_user = user_service.create_user(
            db=db,
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            warehouse_id=target_warehouse_id,
            role_id=user_data.role_id,
        )
        return new_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}",
        )


@router.get("/", response_model=List[UserResponse])
def list_users(
    warehouse_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List users
    Admins can see all users
    Managers can only see users from their warehouse
    Employees cannot see other users
    """
    if current_user.role.name == "employee":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to list users",
        )

    # Determine which users can be seen
    if current_user.role.name == "admin":
        # Admin can specify warehouse_id or see all
        filter_warehouse_id = warehouse_id
    else:
        # Manager can only see their own warehouse
        filter_warehouse_id = current_user.warehouse_id

    users = user_service.get_users(
        db, warehouse_id=filter_warehouse_id, skip=skip, limit=limit
    )
    return users


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get information for a specific user
    """
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Verify permissions
    if current_user.role.name == "employee" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only view your own profile",
        )

    if (
        current_user.role.name == "manager"
        and current_user.warehouse_id != user.warehouse_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only view users from your company",
        )

    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update user information
    """
    target_user = user_service.get_user(db, user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Verify permissions
    if current_user.role.name == "employee" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only update your own profile",
        )

    if (
        current_user.role.name == "manager"
        and current_user.warehouse_id != target_user.warehouse_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only update users from your warehouse",
        )

    # Validate role_id changes - only admin and managers can change roles
    if user_update.role_id is not None and user_update.role_id != target_user.role_id:
        # Only admin and manager can change roles
        if current_user.role.name == "employee":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to change user roles. Only admins and managers can modify roles.",
            )

        # Managers cannot assign admin role (role_id = 1)
        if current_user.role.name == "manager" and user_update.role_id == 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Managers cannot assign admin roles",
            )

    # Validate warehouse_id changes - similar to role restrictions
    if (
        user_update.warehouse_id is not None
        and user_update.warehouse_id != target_user.warehouse_id
    ):
        # Only admin and manager can change warehouse assignments
        if current_user.role.name == "employee":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to change warehouse assignments. Only admins and managers can modify warehouse assignments.",
            )

        # If not admin, can only assign users to their own warehouse
        if (
            current_user.role.name != "admin"
            and user_update.warehouse_id != current_user.warehouse_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Managers can only assign users to their own warehouse",
            )

    # Check if new username already exists
    if user_update.username and user_update.username != target_user.username:
        existing = user_service.get_user_by_username(db, user_update.username)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
            )

    # Check if new email already exists
    if user_update.email and user_update.email != target_user.email:
        existing = user_service.get_user_by_email(db, user_update.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email already taken"
            )

    # Validate password if provided
    if user_update.password:
        try:
            # Use new username/email if provided, otherwise use existing ones
            username_for_validation = user_update.username or target_user.username
            email_for_validation = user_update.email or target_user.email
            PasswordValidator.validate_password(
                user_update.password, username_for_validation, email_for_validation
            )
        except PasswordValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password validation failed: {e.message}",
            )

    updated_user = user_service.update_user(
        db=db,
        user_id=user_id,
        username=user_update.username,
        email=user_update.email,
        password=user_update.password,
        first_name=user_update.first_name,
        last_name=user_update.last_name,
        warehouse_id=user_update.warehouse_id,
        role_id=user_update.role_id,
        is_active=user_update.is_active,
    )

    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a user
    Only admins and managers can delete users
    """
    if current_user.role.name == "employee":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to delete users",
        )

    target_user = user_service.get_user(db, user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Manager can only delete users from their warehouse
    if (
        current_user.role.name == "manager"
        and current_user.warehouse_id != target_user.warehouse_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only delete users from your warehouse",
        )

    success = user_service.delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user",
        )
