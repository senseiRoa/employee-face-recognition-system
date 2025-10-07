from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr

from database import get_db
from services import user_service
from dependencies import get_current_user
from models import User

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
    first_name: str = None
    last_name: str = None
    warehouse_id: int = None
    role_id: int = 3  # Default: employee


class UserUpdateRequest(BaseModel):
    username: str = None
    email: EmailStr = None
    password: str = None
    first_name: str = None
    last_name: str = None
    is_active: bool = None


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
    Create a new user
    Only admins can create users in any warehouse
    Managers can only create users in their warehouse
    """
    # Verify permissions
    if current_user.role.name == "employee":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create users",
        )

    # If not admin, can only create users in their own warehouse
    target_warehouse_id = user_data.warehouse_id or current_user.warehouse_id
    if (
        current_user.role.name != "admin"
        and target_warehouse_id != current_user.warehouse_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only create users in your own warehouse",
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

    updated_user = user_service.update_user(
        db=db,
        user_id=user_id,
        username=user_update.username,
        email=user_update.email,
        password=user_update.password,
        first_name=user_update.first_name,
        last_name=user_update.last_name,
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
