from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from schemas import (
    RegisterFaceReq,
    RegisterFaceRes,
    CheckReq,
    CheckRes,
    Employee,
    EmployeeCreate,
    EmployeeUpdate,
)
from services.face_recognition_service import (
    compute_encoding,
    serialize_encoding,
    deserialize_encoding,
    decide_event,
)
from services import employee_service
from models import Employee as EmployeeModel, FaceEncoding, AccessLog
from dependencies import get_current_user
from utils.permission_decorators import (
    require_employee_read,
    require_employee_write,
    require_employee_delete,
)
from models import User
import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import selectinload

router = APIRouter()

TOLERANCE = 0.6


@router.post("/register_face", response_model=RegisterFaceRes)
def register_face(
    req: RegisterFaceReq,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    employee = employee_service.get_employee(db, req.employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    enc = compute_encoding(req.image_base64)
    enc_s = serialize_encoding(enc)

    new_encoding = FaceEncoding(employee_id=req.employee_id, encoding=enc_s)
    db.add(new_encoding)

    db.commit()
    db.refresh(new_encoding)
    return {
        "status": "ok",
        "employee_id": employee.id,
        "employee_name": f"{employee.first_name} {employee.last_name}",
    }


@router.post("/check_in_out", response_model=CheckRes)
def check_in_out(
    req: CheckReq,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    probe = np.array(compute_encoding(req.image_base64), dtype=np.float32)

    query = select(EmployeeModel).options(selectinload(EmployeeModel.encodings))
    if req.warehouse_id:
        query = query.filter(EmployeeModel.warehouse_id == req.warehouse_id)

    employees = db.execute(query).scalars().all()

    if not employees:
        raise HTTPException(status_code=400, detail="No employees registered.")

    best_id, best_name, best_dist = None, None, 1e9
    for e in employees:
        if not e.encodings:
            continue

        distances = [
            np.linalg.norm(deserialize_encoding(enc.encoding) - probe)
            for enc in e.encodings
        ]
        min_dist = min(distances) if distances else 1e9

        if min_dist < best_dist:
            best_id, best_name, best_dist = (
                e.id,
                f"{e.first_name} {e.last_name}",
                min_dist,
            )

    if best_dist > TOLERANCE:
        return {"recognized": False}

    recognized_employee = next((e for e in employees if e.id == best_id), None)
    if recognized_employee:
        enc_s = serialize_encoding(probe.tolist())
        new_encoding = FaceEncoding(employee_id=best_id, encoding=enc_s)
        db.add(new_encoding)

    event = decide_event(db, best_id)
    log = AccessLog(employee_id=best_id, warehouse_id=req.warehouse_id, event=event)
    db.add(log)
    db.commit()

    return {
        "recognized": True,
        "employee_id": best_id,
        "name": best_name,
        "distance": float(best_dist),
        "event": event,
        "ts": log.ts.isoformat(),
    }


@router.get("/", response_model=List[Employee])
def list_employees(
    warehouse_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employee_read),
):
    """
    List employees with warehouse scope validation
    """
    # Admins can specify warehouse_id, others only from their company
    if current_user.role.name != "admin" and warehouse_id:
        # Verify that the warehouse belongs to their company
        from services import warehouse_service

        warehouse = warehouse_service.get_warehouse(db, warehouse_id)
        if not warehouse or warehouse.company_id != current_user.warehouse.company_id:
            raise HTTPException(
                status_code=403,
                detail="Cannot access employees from warehouses outside your company",
            )

    return employee_service.get_employees(
        db, warehouse_id=warehouse_id, skip=skip, limit=limit
    )


@router.get("/{employee_id}", response_model=Employee)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employee_read),
):
    """
    Get employee details with validation
    """
    employee = employee_service.get_employee(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@router.post("/", response_model=Employee)
def create_employee(
    employee: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employee_write),
):
    """
    Create new employee
    """
    return employee_service.create_employee(db, employee)


@router.put("/{employee_id}", response_model=Employee)
def update_employee(
    employee_id: int,
    employee_update: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employee_write),
):
    """
    Update employee information
    """
    employee = employee_service.update_employee(db, employee_id, employee_update)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@router.delete("/{employee_id}", status_code=204)
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employee_delete),
):
    """
    Delete employee
    """
    success = employee_service.delete_employee(db, employee_id)
    if not success:
        raise HTTPException(status_code=404, detail="Employee not found")
