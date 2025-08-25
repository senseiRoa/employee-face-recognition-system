import base64, io
from PIL import Image
import numpy as np
import face_recognition
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException
from models import AccessLog
import numpy as np

def b64_to_rgb_np(b64: str) -> np.ndarray:
    img_bytes = base64.b64decode(b64)
    img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
    return np.array(img)

def compute_encoding(b64: str) -> List[float]:
    image_np = b64_to_rgb_np(b64)
    boxes = face_recognition.face_locations(image_np, model="hog")
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

def decide_event(session: Session, employee_id: str) -> str:
    last = session.execute(
        select(AccessLog).where(AccessLog.employee_id == employee_id).order_by(AccessLog.ts.desc()).limit(1)
    ).scalar_one_or_none()
    return "out" if (last and last.event == "in") else "in"
