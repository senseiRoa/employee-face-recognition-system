from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine

from database import SessionLocal, DATABASE_URL
from controllers import (
    employees,
    logs,
    auth,
    roles,
    users,
    warehouses,
    companies,
    reports,
)

try:
    from controllers import password

    PASSWORD_CONTROLLER_AVAILABLE = True
except ImportError:
    PASSWORD_CONTROLLER_AVAILABLE = False
    print(
        "Warning: Password controller not available - password management endpoints disabled"
    )

from config.openapi_config import configure_openapi_schema, get_openapi_tags

engine = create_engine(DATABASE_URL, future=True)
print("🚀🚀🚀Engine created")
print(DATABASE_URL)
SessionLocal.configure(bind=engine)

app = FastAPI(
    title="Employee TIME TRACKER",
    version="1.0.0",
    description="API for the facial recognition and employee management system",
    swagger_ui_parameters={
        "persistAuthorization": True,
    },
    openapi_tags=get_openapi_tags(),
)

# Configurar OpenAPI con JWT automáticamente
configure_openapi_schema(app)

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
app.include_router(companies.router, prefix="/companies", tags=["companies"])
app.include_router(roles.router, prefix="/roles", tags=["roles"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(warehouses.router, prefix="/warehouses", tags=["warehouses"])
app.include_router(employees.router, prefix="/employees", tags=["employees"])
app.include_router(logs.router, prefix="/logs", tags=["logs"])
app.include_router(reports.router, prefix="/reports", tags=["reports"])

# Incluir controlador de password si está disponible
if PASSWORD_CONTROLLER_AVAILABLE:
    app.include_router(password.router, tags=["password"])
    print("✅ Password management endpoints enabled")
else:
    print("⚠️ Password management endpoints disabled")


@app.get("/health")
def health():
    return {"status": "ok"}
