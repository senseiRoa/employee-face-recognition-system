from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from schemas import RegisterFaceReq, RegisterFaceRes, CheckReq, CheckRes
from services.face_recognition_service import (
    compute_encoding,
    serialize_encoding,
    deserialize_encoding,
    decide_event,
)
from models import Employee, FaceEncoding, AccessLog
from dependencies import get_current_user
from models import Company
import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import selectinload

router = APIRouter()

TOLERANCE = 0.6


@router.post("/register_face", response_model=RegisterFaceRes)
def register_face(
    req: RegisterFaceReq,
    db: Session = Depends(get_db),
    current_user: Company = Depends(get_current_user),
):
    enc = compute_encoding(req.image_base64)
    enc_s = serialize_encoding(enc)

    emp = db.get(Employee, 0)
    if not emp:
        emp = Employee(name=req.name)
        db.add(emp)
    else:
        emp.name = req.name

    new_encoding = FaceEncoding(encoding=enc_s)
    emp.encodings.append(new_encoding)

    db.commit()
    return {"status": "ok", "employee": req.name}


@router.post("/check_in_out", response_model=CheckRes)
def check_in_out(
    req: CheckReq,
    db: Session = Depends(get_db),
    current_user: Company = Depends(get_current_user),
):
    probe = np.array(compute_encoding(req.image_base64), dtype=np.float32)

    employees = (
        db.execute(select(Employee).options(selectinload(Employee.encodings)))
        .scalars()
        .all()
    )
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
            best_id, best_name, best_dist = e.id, e.name, min_dist

    if best_dist > TOLERANCE:
        return {"recognized": False}

    recognized_employee = next((e for e in employees if e.id == best_id), None)
    if recognized_employee:
        enc_s = serialize_encoding(probe.tolist())
        new_encoding = FaceEncoding(encoding=enc_s)
        recognized_employee.encodings.append(new_encoding)

    event = decide_event(db, best_id)
    log = AccessLog(employee_id=best_id, event=event)
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


@router.get("/employees")
def list_employees(
    db: Session = Depends(get_db), current_user: Company = Depends(get_current_user)
):
    rows = db.execute(select(Employee)).scalars().all()
    return [{"employee_id": r.id, "name": r.name} for r in rows]
