from fastapi import FastAPI
from infrastructure.api.routes import employees, logs, recognition, auth_routes

app = FastAPI()

app.include_router(employees.router)
app.include_router(logs.router)
app.include_router(recognition.router)
app.include_router(auth_routes.router)
