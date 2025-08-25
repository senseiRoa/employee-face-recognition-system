from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Literal
import base64, io, os, datetime
from PIL import Image
import numpy as np
import face_recognition

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, select, text
from sqlalchemy.orm import declarative_base, Session, relationship

# --- Config ---
DB_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "db.sqlite3")
engine = create_engine(f"sqlite:///{DB_PATH}", future=True)
Base = declarative_base()

# --- Modelos DB ---
class Employee(Base):
    __tablename__ = "employees"
    id = Column(String, primary_key=True)  # employee_id definido por el cliente
    name = Column(String, nullable=False)
    # encoding almacenado como texto JSON de floats separados por coma (simple para POC)
    encoding = Column(String, nullable=False)  # "0.12,0.34,..."

    logs = relationship("AccessLog", back_populates="employee")

class AccessLog(Base):
    __tablename__ = "access_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String, ForeignKey("employees.id"), nullable=False)
    event = Column(String, nullable=False)  # "in" | "out"
    ts = Column(DateTime, default=datetime.datetime.utcnow)

    employee = relationship("Employee", back_populates="logs")

Base.metadata.create_all(engine)

# --- FastAPI ---
app = FastAPI(title="Employee Face POC")

origins = [
    "http://localhost",
    "http://localhost:8100",      # Ionic serve
    "capacitor://localhost",
    "ionic://localhost",
    "http://10.0.2.2:8100",       # Emulador Android (opcional)
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Schemas ---
class RegisterFaceReq(BaseModel):
    employee_id: str
    name: str
    image_base64: str  # sin el prefijo data:image/...

class RegisterFaceRes(BaseModel):
    status: Literal["ok"]
    employee_id: str

class CheckReq(BaseModel):
    image_base64: str

class CheckRes(BaseModel):
    recognized: bool
    employee_id: Optional[str] = None
    name: Optional[str] = None
    distance: Optional[float] = None
    event: Optional[Literal["in","out"]] = None
    ts: Optional[str] = None

# --- Utilidades ---
def b64_to_rgb_np(b64: str) -> np.ndarray:
    img_bytes = base64.b64decode(b64)
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    return np.array(img)

def compute_encoding(b64: str) -> List[float]:
    image_np = b64_to_rgb_np(b64)
    boxes = face_recognition.face_locations(image_np, model="hog")  # HOG para POC (sin GPU)
    if not boxes:
        raise HTTPException(status_code=422, detail="No se detectó rostro en la imagen.")
    encs = face_recognition.face_encodings(image_np, boxes)
    if not encs:
        raise HTTPException(status_code=422, detail="No se pudo extraer el encoding del rostro.")
    return encs[0].tolist()

def serialize_encoding(enc: List[float]) -> str:
    return ",".join(f"{v:.8f}" for v in enc)

def deserialize_encoding(s: str) -> np.ndarray:
    return np.array([float(x) for x in s.split(",")], dtype=np.float32)

TOLERANCE = 0.6

def decide_event(session: Session, employee_id: str) -> str:
    last = session.execute(
        select(AccessLog).where(AccessLog.employee_id == employee_id).order_by(AccessLog.ts.desc()).limit(1)
    ).scalar_one_or_none()
    return "out" if (last and last.event == "in") else "in"

# --- Endpoints ---
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
            # Distancia euclidiana (face_recognition usa distancia similar)
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