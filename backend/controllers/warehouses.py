from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from schemas import Warehouse, WarehouseCreate, WarehouseUpdate
from services import warehouse_service
from dependencies import get_current_user
from models import User

router = APIRouter()


@router.post("/", response_model=Warehouse, status_code=status.HTTP_201_CREATED)
def create_warehouse(
    warehouse: WarehouseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Only admins and managers can create warehouses
    if current_user.role.name == "employee":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create warehouses",
        )

    # If not admin, can only create warehouses in their own company
    target_company_id = (
        warehouse.company_id
        if hasattr(warehouse, "company_id")
        else current_user.company_id
    )
    if (
        current_user.role.name != "admin"
        and target_company_id != current_user.company_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only create warehouses in your own company",
        )

    return warehouse_service.create_warehouse(db, warehouse)


@router.get("/", response_model=List[Warehouse])
def list_warehouses(
    company_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Determine which warehouses the user can see
    if current_user.role.name == "admin":
        # Admin puede especificar company_id o ver todos
        filter_company_id = company_id
    else:
        # Other roles can only see warehouses from their company
        filter_company_id = current_user.company_id

    return warehouse_service.get_warehouses(
        db, company_id=filter_company_id, skip=skip, limit=limit
    )


@router.get("/{warehouse_id}", response_model=Warehouse)
def get_warehouse(
    warehouse_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    warehouse = warehouse_service.get_warehouse(db, warehouse_id)
    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Warehouse not found"
        )

    # Verify permissions: only admin or users from the same company
    if (
        current_user.role.name != "admin"
        and warehouse.company_id != current_user.company_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access this warehouse",
        )

    return warehouse


@router.put("/{warehouse_id}", response_model=Warehouse)
def update_warehouse(
    warehouse_id: int,
    warehouse_update: WarehouseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    warehouse = warehouse_service.update_warehouse(db, warehouse_id, warehouse_update)
    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Warehouse not found"
        )
    return warehouse


@router.delete("/{warehouse_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_warehouse(
    warehouse_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify warehouse exists and user has access
    warehouse = warehouse_service.get_warehouse(db, warehouse_id)
    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Warehouse not found"
        )

    # Verify permissions: only admin or users from the same company can delete
    if (
        current_user.role.name != "admin"
        and warehouse.company_id != current_user.company_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to delete this warehouse",
        )

    # Check for associated users and employees
    user_count, employee_count = warehouse_service.check_warehouse_dependencies(
        db, warehouse_id
    )

    if user_count > 0 or employee_count > 0:
        details = []
        if user_count > 0:
            details.append(f"{user_count} user(s)")
        if employee_count > 0:
            details.append(f"{employee_count} employee(s)")

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot delete warehouse. It has {' and '.join(details)} associated. Please remove or reassign them first.",
        )

    success = warehouse_service.delete_warehouse(db, warehouse_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Warehouse not found"
        )
