from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select

from database import engine, Base
from models import Employee, AccessLog, FaceEncoding
from schemas import RegisterFaceReq, RegisterFaceRes, CheckReq, CheckRes
from services import compute_encoding, serialize_encoding, deserialize_encoding, decide_event
import numpy as np

Base.metadata.create_all(engine)

app = FastAPI(title="Employee Face POC")

origins = [
    "http://localhost",
    "https://localhost",
    "http://localhost:8100",   # Ionic local dev
    "capacitor://localhost",   # App en Android/iOS
    "http://localhost:4200",   # Angular local
    "https://tudominio.com",   # Producción
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TOLERANCE = 0.6

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/register_face", response_model=RegisterFaceRes)
def register_face(req: RegisterFaceReq):
    enc = compute_encoding(req.image_base64)
    enc_s = serialize_encoding(enc)
    with Session(engine) as session:
        emp = session.get(Employee, req.employee_id)
        if not emp:
            emp = Employee(id=req.employee_id, name=req.name)
            session.add(emp)
        else:
            emp.name = req.name

        new_encoding = FaceEncoding(encoding=enc_s)
        emp.encodings.append(new_encoding)
        
        session.commit()
    return {"status": "ok", "employee_id": req.employee_id}

@app.post("/check_in_out", response_model=CheckRes)
def check_in_out(req: CheckReq):
    probe = np.array(compute_encoding(req.image_base64), dtype=np.float32)

    with Session(engine) as session:
        employees = session.execute(
            select(Employee).options(selectinload(Employee.encodings))
        ).scalars().all()
        if not employees:
            raise HTTPException(status_code=400, detail="No hay empleados registrados.")

        best_id, best_name, best_dist = None, None, 1e9
        for e in employees:
            if not e.encodings:
                continue
            
            distances = [np.linalg.norm(deserialize_encoding(enc.encoding) - probe) for enc in e.encodings]
            min_dist = min(distances) if distances else 1e9

            if min_dist < best_dist:
                best_id, best_name, best_dist = e.id, e.name, min_dist

        if best_dist > TOLERANCE:
            return {"recognized": False}

        # Add new encoding for recognized user
        recognized_employee = next((e for e in employees if e.id == best_id), None)
        if recognized_employee:
            enc_s = serialize_encoding(probe.tolist())
            new_encoding = FaceEncoding(encoding=enc_s)
            recognized_employee.encodings.append(new_encoding)

        event = decide_event(session, best_id)
        log = AccessLog(employee_id=best_id, event=event)
        session.add(log)
        session.commit()

        return {
            "recognized": True,
            "employee_id": best_id,
            "name": best_name,
            "distance": float(best_dist),
            "event": event,
            "ts": log.ts.isoformat()
        }

@app.get("/employees")
def list_employees():
    with Session(engine) as session:
        rows = session.execute(select(Employee)).scalars().all()
        return [{"employee_id": r.id, "name": r.name} for r in rows]

@app.get("/logs")
def list_logs():
    with Session(engine) as session:
        rows = session.execute(
            select(AccessLog).order_by(AccessLog.ts.desc()).limit(100)
        ).scalars().all()
        return [{"id": r.id, "employee_id": r.employee_id, "event": r.event, "ts": r.ts.isoformat()} for r in rows]