from sqlalchemy.orm import Session
from typing import List, Optional
from models import Employee
from schemas import EmployeeCreate, EmployeeUpdate


def create_employee(db: Session, employee: EmployeeCreate) -> Employee:
    db_employee = Employee(**employee.dict())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


def get_employee(db: Session, employee_id: int) -> Optional[Employee]:
    return db.query(Employee).filter(Employee.id == employee_id).first()


def get_employees(db: Session, warehouse_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Employee]:
    query = db.query(Employee)
    if warehouse_id:
        query = query.filter(Employee.warehouse_id == warehouse_id)
    return query.offset(skip).limit(limit).all()


def update_employee(db: Session, employee_id: int, employee_update: EmployeeUpdate) -> Optional[Employee]:
    db_employee = get_employee(db, employee_id)
    if not db_employee:
        return None
    
    update_data = employee_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_employee, key, value)
    
    db.commit()
    db.refresh(db_employee)
    return db_employee


def delete_employee(db: Session, employee_id: int) -> bool:
    db_employee = get_employee(db, employee_id)
    if not db_employee:
        return False
    
    db.delete(db_employee)
    db.commit()
    return True
