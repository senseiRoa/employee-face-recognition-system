from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select

from database import engine, Base
from models import Employee, AccessLog
from schemas import RegisterFaceReq, RegisterFaceRes, CheckReq, CheckRes
from services import compute_encoding, serialize_encoding, deserialize_encoding, decide_event
import numpy as np

Base.metadata.create_all(engine)

app = FastAPI(title="Employee Face POC")

origins = [
    "http://localhost",
    "http://localhost:8100",
    "capacitor://localhost",
    "ionic://localhost",
    "http://10.0.2.2:8100",
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
        if emp:
            emp.name = req.name
            emp.encoding = enc_s
        else:
            emp = Employee(id=req.employee_id, name=req.name, encoding=enc_s)
            session.add(emp)
        session.commit()
    return {"status": "ok", "employee_id": req.employee_id}

@app.post("/check_in_out", response_model=CheckRes)
def check_in_out(req: CheckReq):
    probe = np.array(compute_encoding(req.image_base64), dtype=np.float32)

    with Session(engine) as session:
        employees = session.execute(select(Employee)).scalars().all()
        if not employees:
            raise HTTPException(status_code=400, detail="No hay empleados registrados.")

        best_id, best_name, best_dist = None, None, 1e9
        for e in employees:
            db_enc = deserialize_encoding(e.encoding)
            dist = np.linalg.norm(db_enc - probe)
            if dist < best_dist:
                best_id, best_name, best_dist = e.id, e.name, dist

        if best_dist > TOLERANCE:
            return {"recognized": False}

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
