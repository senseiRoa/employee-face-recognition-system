"""
Configuración de OpenAPI/Swagger para la API
"""

from typing import Dict, Any
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def configure_openapi_schema(app: FastAPI) -> None:
    """
    Configura el esquema OpenAPI personalizado para JWT authentication
    """

    def custom_openapi() -> Dict[str, Any]:
        if app.openapi_schema:
            return app.openapi_schema

        # Generar el esquema base automáticamente
        openapi_schema = get_openapi(
            title=app.title,
            version=getattr(app, "version", "1.0.0"),
            description=getattr(app, "description", ""),
            routes=app.routes,
            tags=getattr(app, "openapi_tags", None),
        )

        # Configurar únicamente el esquema de seguridad JWT
        if "components" not in openapi_schema:
            openapi_schema["components"] = {}

        openapi_schema["components"]["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Ingrese el token JWT obtenido del endpoint /auth/login",
            }
        }

        # NO aplicar seguridad global - dejar que FastAPI maneje esto automáticamente
        # basado en las dependencias de cada endpoint

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    # Asignar la función personalizada a la app
    app.openapi = custom_openapi


def get_openapi_tags() -> list:
    """
    Returns a list of predefined tags to organize and describe different groups of endpoints in the OpenAPI documentation.
    These tags facilitate navigation and understanding of the available API operations by grouping endpoints by functionality.
    They can be extended or modified according to the project's needs.
    """
    return [
        {
            "name": "auth",
            "description": "Operations related to authentication and JWT token management.",
        },
        {"name": "companies", "description": "Company management and administration."},
        {"name": "roles", "description": "User roles and permissions management."},
        {"name": "users", "description": "User administration and profile management."},
        {
            "name": "warehouses",
            "description": "Warehouse management and associated resources.",
        },
        {
            "name": "tablets",
            "description": "Administration and control of tablets registered in the system.",
        },
        {
            "name": "employees",
            "description": "Employee management and relevant information.",
        },
        {
            "name": "logs",
            "description": "Operations to query and manage activity logs.",
        },
        {
            "name": "dashboard",
            "description": "Dashboard statistics and data visualization endpoints.",
        },
        {"name": "reports", "description": "System report generation and queries."},
    ]
