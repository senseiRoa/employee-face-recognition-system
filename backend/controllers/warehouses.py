from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from schemas import Warehouse, WarehouseCreate, WarehouseUpdate
from services import warehouse_service
from dependencies import get_current_user
from models import Company

router = APIRouter()


@router.post("/", response_model=Warehouse, status_code=status.HTTP_201_CREATED)
def create_warehouse(
    warehouse: WarehouseCreate,
    db: Session = Depends(get_db),
    current_user: Company = Depends(get_current_user)
):
    return warehouse_service.create_warehouse(db, warehouse)


@router.get("/", response_model=List[Warehouse])
def list_warehouses(
    company_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Company = Depends(get_current_user)
):
    return warehouse_service.get_warehouses(db, company_id=company_id, skip=skip, limit=limit)


@router.get("/{warehouse_id}", response_model=Warehouse)
def get_warehouse(
    warehouse_id: int,
    db: Session = Depends(get_db),
    current_user: Company = Depends(get_current_user)
):
    warehouse = warehouse_service.get_warehouse(db, warehouse_id)
    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found"
        )
    return warehouse


@router.put("/{warehouse_id}", response_model=Warehouse)
def update_warehouse(
    warehouse_id: int,
    warehouse_update: WarehouseUpdate,
    db: Session = Depends(get_db),
    current_user: Company = Depends(get_current_user)
):
    warehouse = warehouse_service.update_warehouse(db, warehouse_id, warehouse_update)
    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found"
        )
    return warehouse


@router.delete("/{warehouse_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_warehouse(
    warehouse_id: int,
    db: Session = Depends(get_db),
    current_user: Company = Depends(get_current_user)
):
    success = warehouse_service.delete_warehouse(db, warehouse_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found"
        )
