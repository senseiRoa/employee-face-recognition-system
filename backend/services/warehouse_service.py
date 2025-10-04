from sqlalchemy.orm import Session
from typing import List, Optional
from models import Warehouse
from schemas import WarehouseCreate, WarehouseUpdate


def create_warehouse(db: Session, warehouse: WarehouseCreate) -> Warehouse:
    db_warehouse = Warehouse(**warehouse.dict())
    db.add(db_warehouse)
    db.commit()
    db.refresh(db_warehouse)
    return db_warehouse


def get_warehouse(db: Session, warehouse_id: int) -> Optional[Warehouse]:
    return db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()


def get_warehouses(db: Session, company_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Warehouse]:
    query = db.query(Warehouse)
    if company_id:
        query = query.filter(Warehouse.company_id == company_id)
    return query.offset(skip).limit(limit).all()


def update_warehouse(db: Session, warehouse_id: int, warehouse_update: WarehouseUpdate) -> Optional[Warehouse]:
    db_warehouse = get_warehouse(db, warehouse_id)
    if not db_warehouse:
        return None
    
    update_data = warehouse_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_warehouse, key, value)
    
    db.commit()
    db.refresh(db_warehouse)
    return db_warehouse


def delete_warehouse(db: Session, warehouse_id: int) -> bool:
    db_warehouse = get_warehouse(db, warehouse_id)
    if not db_warehouse:
        return False
    
    db.delete(db_warehouse)
    db.commit()
    return True
