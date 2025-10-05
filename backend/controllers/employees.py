from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from schemas import RegisterFaceReq, RegisterFaceRes, CheckReq, CheckRes, Employee, EmployeeCreate, EmployeeUpdate
from services.face_recognition_service import (
    compute_encoding,
    serialize_encoding,
    deserialize_encoding,
    decide_event,
)
from services import employee_service
from models import Employee as EmployeeModel, FaceEncoding, AccessLog
from dependencies import get_current_user
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
    enc = compute_encoding(req.image_base64)
    enc_s = serialize_encoding(enc)

    emp = EmployeeModel(
        warehouse_id=req.warehouse_id,
        first_name=req.first_name,
        last_name=req.last_name,
        email=req.email
    )
    db.add(emp)
    db.flush()

    new_encoding = FaceEncoding(employee_id=emp.id, encoding=enc_s)
    db.add(new_encoding)
    
    db.commit()
    db.refresh(emp)
    
    return {
        "status": "ok",
        "employee_id": emp.id,
        "employee_name": f"{emp.first_name} {emp.last_name}"
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
        raise HTTPException(status_code=400, detail="No hay empleados registrados.")

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
            best_id, best_name, best_dist = e.id, f"{e.first_name} {e.last_name}", min_dist

    if best_dist > TOLERANCE:
        return {"recognized": False}

    recognized_employee = next((e for e in employees if e.id == best_id), None)
    if recognized_employee:
        enc_s = serialize_encoding(probe.tolist())
        new_encoding = FaceEncoding(employee_id=best_id, encoding=enc_s)
        db.add(new_encoding)

    event = decide_event(db, best_id)
    log = AccessLog(
        employee_id=best_id,
        warehouse_id=req.warehouse_id,
        event=event
    )
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
    current_user: User = Depends(get_current_user)
):
    return employee_service.get_employees(db, warehouse_id=warehouse_id, skip=skip, limit=limit)


@router.get("/{employee_id}", response_model=Employee)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    employee = employee_service.get_employee(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@router.post("/", response_model=Employee)
def create_employee(
    employee: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return employee_service.create_employee(db, employee)


@router.put("/{employee_id}", response_model=Employee)
def update_employee(
    employee_id: int,
    employee_update: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    employee = employee_service.update_employee(db, employee_id, employee_update)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@router.delete("/{employee_id}", status_code=204)
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    success = employee_service.delete_employee(db, employee_id)
    if not success:
        raise HTTPException(status_code=404, detail="Employee not found")

