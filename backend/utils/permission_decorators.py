"""
Sistema de decoradores y dependencias para validación de permisos en FastAPI
"""

from functools import wraps
from typing import Callable
from fastapi import HTTPException, status, Depends

from models import User
from dependencies import get_current_user
from utils.permissions import (
    Permission,
    Action,
    validate_role_permissions,
    can_read_warehouses,
    can_write_warehouses,
    can_delete_warehouses,
    can_read_employees,
    can_write_employees,
    can_delete_employees,
    can_read_users,
    can_write_users,
    can_delete_users,
    can_read_companies,
    can_write_companies,
    can_delete_companies,
    can_read_reports,
    can_export_reports,
    can_read_logs,
    can_audit_logs,
)


def require_permission(permission: Permission, action: Action):
    """
    Decorador para validar permisos en endpoints de FastAPI

    Args:
        permission: Permiso requerido
        action: Acción requerida

    Usage:
        @require_permission(Permission.USER_MANAGEMENT, Action.WRITE)
        def create_user(...)
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Buscar current_user en los argumentos
            current_user = None
            for key, value in kwargs.items():
                if isinstance(value, User):
                    current_user = value
                    break

            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            # Validar permisos
            has_perm, error_msg = validate_role_permissions(
                current_user.role.name, permission, action
            )

            if not has_perm:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail=error_msg
                )

            return func(*args, **kwargs)

        return wrapper

    return decorator


# Dependencias FastAPI para validaciones comunes
def require_warehouse_read(current_user: User = Depends(get_current_user)) -> User:
    """Dependencia que requiere permisos de lectura de warehouses"""
    if not can_read_warehouses(current_user.role.name):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Required: Read access to Warehouse Access",
        )
    return current_user


def require_warehouse_write(current_user: User = Depends(get_current_user)) -> User:
    """Dependencia que requiere permisos de escritura de warehouses"""
    if not can_write_warehouses(current_user.role.name):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Required: Write access to Warehouse Access",
        )
    return current_user


def require_warehouse_delete(current_user: User = Depends(get_current_user)) -> User:
    """Dependencia que requiere permisos de eliminación de warehouses"""
    if not can_delete_warehouses(current_user.role.name):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Required: Delete access to Warehouse Access",
        )
    return current_user


def require_employee_read(current_user: User = Depends(get_current_user)) -> User:
    """Dependencia que requiere permisos de lectura de empleados"""
    if not can_read_employees(current_user.role.name):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Required: Read access to Employee Management",
        )
    return current_user


def require_employee_write(current_user: User = Depends(get_current_user)) -> User:
    """Dependencia que requiere permisos de escritura de empleados"""
    if not can_write_employees(current_user.role.name):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Required: Write access to Employee Management",
        )
    return current_user


def require_employee_delete(current_user: User = Depends(get_current_user)) -> User:
    """Dependencia que requiere permisos de eliminación de empleados"""
    if not can_delete_employees(current_user.role.name):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Required: Delete access to Employee Management",
        )
    return current_user


def require_user_read(current_user: User = Depends(get_current_user)) -> User:
    """Dependencia que requiere permisos de lectura de usuarios"""
    if not can_read_users(current_user.role.name):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Required: Read access to User Management",
        )
    return current_user


def require_user_write(current_user: User = Depends(get_current_user)) -> User:
    """Dependencia que requiere permisos de escritura de usuarios"""
    if not can_write_users(current_user.role.name):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Required: Write access to User Management",
        )
    return current_user


def require_user_delete(current_user: User = Depends(get_current_user)) -> User:
    """Dependencia que requiere permisos de eliminación de usuarios"""
    if not can_delete_users(current_user.role.name):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Required: Delete access to User Management",
        )
    return current_user


def require_company_read(current_user: User = Depends(get_current_user)) -> User:
    """Dependencia que requiere permisos de lectura de empresas"""
    if not can_read_companies(current_user.role.name):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Required: Read access to Company Management",
        )
    return current_user


def require_company_write(current_user: User = Depends(get_current_user)) -> User:
    """Dependencia que requiere permisos de escritura de empresas"""
    if not can_write_companies(current_user.role.name):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Required: Write access to Company Management",
        )
    return current_user


def require_company_delete(current_user: User = Depends(get_current_user)) -> User:
    """Dependencia que requiere permisos de eliminación de empresas"""
    if not can_delete_companies(current_user.role.name):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Required: Delete access to Company Management",
        )
    return current_user


def require_reports_read(current_user: User = Depends(get_current_user)) -> User:
    """Dependencia que requiere permisos de lectura de reportes"""
    if not can_read_reports(current_user.role.name):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Required: Read access to Reports Analytics",
        )
    return current_user


def require_reports_export(current_user: User = Depends(get_current_user)) -> User:
    """Dependencia que requiere permisos de exportación de reportes"""
    if not can_export_reports(current_user.role.name):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Required: Export access to Reports Analytics",
        )
    return current_user


def require_logs_read(current_user: User = Depends(get_current_user)) -> User:
    """Dependencia que requiere permisos de lectura de logs"""
    if not can_read_logs(current_user.role.name):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Required: Read access to System Logs",
        )
    return current_user


def require_logs_audit(current_user: User = Depends(get_current_user)) -> User:
    """Dependencia que requiere permisos de auditoría de logs"""
    if not can_audit_logs(current_user.role.name):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Required: Audit access to System Logs",
        )
    return current_user


def require_dashboard_read(current_user: User = Depends(get_current_user)) -> User:
    """Dependencia que requiere permisos de lectura de dashboard"""
    if not can_read_reports(current_user.role.name):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Required: Read access to Dashboard Analytics",
        )
    return current_user


def require_reports_analytics_read(current_user: User = Depends(get_current_user)) -> User:
    """Dependencia que requiere permisos de lectura de reportes y analytics"""
    if not can_read_reports(current_user.role.name):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Required: Read access to Reports Analytics",
        )
    return current_user


# Funciones helper para validaciones contextuales
def validate_warehouse_scope(current_user: User, target_warehouse_id: int) -> bool:
    """
    Valida si el usuario puede acceder a un warehouse específico
    - Admin: puede acceder a todos
    - Manager: solo su warehouse
    - Employee: solo su warehouse
    """
    if current_user.role.name == "admin":
        return True

    return current_user.warehouse_id == target_warehouse_id


def validate_company_scope(current_user: User, target_company_id: int) -> bool:
    """
    Valida si el usuario puede acceder a una empresa específica
    - Admin: puede acceder a todas
    - Manager/Employee: solo su empresa
    """
    if current_user.role.name == "admin":
        return True

    return current_user.warehouse.company_id == target_company_id


def get_accessible_warehouse_ids(current_user: User) -> list[int]:
    """
    Obtiene los IDs de warehouses a los que el usuario tiene acceso
    """
    if current_user.role.name == "admin":
        # Admin puede acceder a todos los warehouses
        # Esto debería implementarse consultando la BD
        return []  # Retornar lista vacía significa "todos"

    # Manager y Employee solo su warehouse
    return [current_user.warehouse_id]


def get_accessible_company_ids(current_user: User) -> list[int]:
    """
    Obtiene los IDs de empresas a las que el usuario tiene acceso
    """
    if current_user.role.name == "admin":
        # Admin puede acceder a todas las empresas
        return []  # Lista vacía significa "todas"

    # Manager y Employee solo su empresa
    return [current_user.warehouse.company_id]
