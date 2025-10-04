from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine

from database import Base, SessionLocal, DATABASE_URL
from controllers import employees, logs, auth

engine = create_engine(DATABASE_URL, future=True)
print("🚀🚀🚀Engine created")
print(DATABASE_URL)
SessionLocal.configure(bind=engine)

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

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(employees.router, prefix="/employees", tags=["employees"])
app.include_router(logs.router, prefix="/logs", tags=["logs"])

@app.get("/health")
def health():
    return {"status": "ok"}