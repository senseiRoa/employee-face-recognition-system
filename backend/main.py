from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, create_engine

from database import Base, SessionLocal, DATABASE_URL
from models import Employee, AccessLog, FaceEncoding
from schemas import RegisterFaceReq, RegisterFaceRes, CheckReq, CheckRes
from services import (
    compute_encoding,
    serialize_encoding,
    deserialize_encoding,
    decide_event,
)
import numpy as np

engine = create_engine(DATABASE_URL, future=True)
print("🚀🚀🚀Engine created")
print(DATABASE_URL)
SessionLocal.configure(bind=engine)

# Base.metadata.create_all(engine) # No longer needed with Alembic

app = FastAPI(title="Employee-TIME-TRACKER")

origins = [
    "http://localhost",
    "https://localhost",
    "http://localhost:8100",  # Ionic local dev
    "http://localhost:8101",  # Ionic local dev
    "capacitor://localhost",  # App en Android/iOS
    "http://localhost:4200",  # Angular local
    "https://tudominio.com",  # Producción
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


TOLERANCE = 0.6


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/register_face", response_model=RegisterFaceRes)
def register_face(req: RegisterFaceReq, db: Session = Depends(get_db)):
    enc = compute_encoding(req.image_base64)
    enc_s = serialize_encoding(enc)

    emp = db.get(Employee, req.employee_id)
    if not emp:
        emp = Employee(id=req.employee_id, name=req.name)
        db.add(emp)
    else:
        emp.name = req.name

    new_encoding = FaceEncoding(encoding=enc_s)
    emp.encodings.append(new_encoding)

    db.commit()
    return {"status": "ok", "employee_id": req.employee_id}


@app.post("/check_in_out", response_model=CheckRes)
def check_in_out(req: CheckReq, db: Session = Depends(get_db)):
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

    # Add new encoding for recognized user
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


@app.get("/employees")
def list_employees(db: Session = Depends(get_db)):
    rows = db.execute(select(Employee)).scalars().all()
    return [{"employee_id": r.id, "name": r.name} for r in rows]


@app.get("/logs")
def list_logs(db: Session = Depends(get_db)):
    rows = (
        db.execute(select(AccessLog).order_by(AccessLog.ts.desc()).limit(100))
        .scalars()
        .all()
    )
    return [
        {
            "id": r.id,
            "employee_id": r.employee_id,
            "event": r.event,
            "ts": r.ts.isoformat(),
        }
        for r in rows
    ]
