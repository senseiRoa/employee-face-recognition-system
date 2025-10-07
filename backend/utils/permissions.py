"""
Sistema de permisos granular para el control de acceso basado en roles.
"""

from enum import Enum
from typing import Dict, List, Set
from dataclasses import dataclass


class Permission(Enum):
    """Enum de permisos disponibles en el sistema"""

    WAREHOUSE_ACCESS = "warehouse_access"
    EMPLOYEE_MANAGEMENT = "employee_management"
    USER_MANAGEMENT = "user_management"
    COMPANY_MANAGEMENT = "company_management"
    REPORTS_ANALYTICS = "reports_analytics"
    SYSTEM_LOGS = "system_logs"


class Action(Enum):
    """Enum de acciones que se pueden realizar"""

    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXPORT = "export"
    AUDIT = "audit"


@dataclass
class PermissionSet:
    """Representa un conjunto de permisos con sus acciones"""

    permission: Permission
    actions: Set[Action]

    def has_action(self, action: Action) -> bool:
        """Verifica si este conjunto de permisos incluye la acción especificada"""
        return action in self.actions


# Definición de permisos por rol
ROLE_PERMISSIONS: Dict[str, List[PermissionSet]] = {
    "admin": [
        # Admin tiene acceso completo a todo
        PermissionSet(
            Permission.WAREHOUSE_ACCESS, {Action.READ, Action.WRITE, Action.DELETE}
        ),
        PermissionSet(
            Permission.EMPLOYEE_MANAGEMENT, {Action.READ, Action.WRITE, Action.DELETE}
        ),
        PermissionSet(
            Permission.USER_MANAGEMENT, {Action.READ, Action.WRITE, Action.DELETE}
        ),
        PermissionSet(
            Permission.COMPANY_MANAGEMENT, {Action.READ, Action.WRITE, Action.DELETE}
        ),
        PermissionSet(
            Permission.REPORTS_ANALYTICS,
            {Action.READ, Action.WRITE, Action.DELETE, Action.EXPORT},
        ),
        PermissionSet(Permission.SYSTEM_LOGS, {Action.READ, Action.AUDIT}),
    ],
    "manager": [
        # Manager tiene acceso limitado a su warehouse
        PermissionSet(Permission.WAREHOUSE_ACCESS, {Action.READ, Action.WRITE}),
        PermissionSet(
            Permission.EMPLOYEE_MANAGEMENT, {Action.READ, Action.WRITE, Action.DELETE}
        ),
        PermissionSet(
            Permission.USER_MANAGEMENT, {Action.READ, Action.WRITE}
        ),  # No puede eliminar usuarios
        PermissionSet(
            Permission.COMPANY_MANAGEMENT, {Action.READ, Action.WRITE}
        ),  # Solo su empresa
        PermissionSet(Permission.REPORTS_ANALYTICS, {Action.READ, Action.EXPORT}),
        PermissionSet(Permission.SYSTEM_LOGS, {Action.READ}),
    ],
    "employee": [
        # Employee solo lectura
        PermissionSet(Permission.WAREHOUSE_ACCESS, {Action.READ}),
        PermissionSet(
            Permission.EMPLOYEE_MANAGEMENT, {Action.READ}
        ),  # Solo ver empleados
        PermissionSet(Permission.COMPANY_MANAGEMENT, {Action.READ}),  # Solo su empresa
        PermissionSet(
            Permission.REPORTS_ANALYTICS, {Action.READ}
        ),  # Solo ver reportes básicos
        # No acceso a user management, company management, ni system logs
    ],
}


def get_role_permissions(role_name: str) -> List[PermissionSet]:
    """
    Obtiene los permisos de un rol específico

    Args:
        role_name: Nombre del rol (admin, manager, employee)

    Returns:
        Lista de conjuntos de permisos para el rol
    """
    return ROLE_PERMISSIONS.get(role_name.lower(), [])


def has_permission(role_name: str, permission: Permission, action: Action) -> bool:
    """
    Verifica si un rol tiene un permiso específico con una acción específica

    Args:
        role_name: Nombre del rol
        permission: Permiso a verificar
        action: Acción a verificar

    Returns:
        True si el rol tiene el permiso y la acción
    """
    role_permissions = get_role_permissions(role_name)

    for perm_set in role_permissions:
        if perm_set.permission == permission:
            return perm_set.has_action(action)

    return False


def get_permissions_json(role_name: str) -> dict:
    """
    Convierte los permisos de un rol a formato JSON para almacenar en BD

    Args:
        role_name: Nombre del rol

    Returns:
        Dict con estructura JSON de permisos
    """
    role_permissions = get_role_permissions(role_name)
    json_permissions = {}

    for perm_set in role_permissions:
        permission_key = perm_set.permission.value
        actions_list = [action.value for action in perm_set.actions]
        json_permissions[permission_key] = actions_list

    return json_permissions


def validate_role_permissions(
    role_name: str, required_permission: Permission, required_action: Action
) -> tuple[bool, str]:
    """
    Valida si un rol tiene los permisos requeridos y devuelve mensaje de error si no

    Args:
        role_name: Nombre del rol
        required_permission: Permiso requerido
        required_action: Acción requerida

    Returns:
        Tuple (tiene_permiso: bool, mensaje_error: str)
    """
    if not has_permission(role_name, required_permission, required_action):
        action_name = required_action.value.title()
        permission_name = required_permission.value.replace("_", " ").title()

        return (
            False,
            f"Insufficient permissions. Required: {action_name} access to {permission_name}",
        )

    return True, ""


# Funciones de conveniencia para validaciones comunes
def can_read_warehouses(role_name: str) -> bool:
    """Verifica si puede leer warehouses"""
    return has_permission(role_name, Permission.WAREHOUSE_ACCESS, Action.READ)


def can_write_warehouses(role_name: str) -> bool:
    """Verifica si puede crear/editar warehouses"""
    return has_permission(role_name, Permission.WAREHOUSE_ACCESS, Action.WRITE)


def can_delete_warehouses(role_name: str) -> bool:
    """Verifica si puede eliminar warehouses"""
    return has_permission(role_name, Permission.WAREHOUSE_ACCESS, Action.DELETE)


def can_read_employees(role_name: str) -> bool:
    """Verifica si puede leer empleados"""
    return has_permission(role_name, Permission.EMPLOYEE_MANAGEMENT, Action.READ)


def can_write_employees(role_name: str) -> bool:
    """Verifica si puede crear/editar empleados"""
    return has_permission(role_name, Permission.EMPLOYEE_MANAGEMENT, Action.WRITE)


def can_delete_employees(role_name: str) -> bool:
    """Verifica si puede eliminar empleados"""
    return has_permission(role_name, Permission.EMPLOYEE_MANAGEMENT, Action.DELETE)


def can_read_users(role_name: str) -> bool:
    """Verifica si puede leer usuarios"""
    return has_permission(role_name, Permission.USER_MANAGEMENT, Action.READ)


def can_write_users(role_name: str) -> bool:
    """Verifica si puede crear/editar usuarios"""
    return has_permission(role_name, Permission.USER_MANAGEMENT, Action.WRITE)


def can_delete_users(role_name: str) -> bool:
    """Verifica si puede eliminar usuarios"""
    return has_permission(role_name, Permission.USER_MANAGEMENT, Action.DELETE)


def can_read_companies(role_name: str) -> bool:
    """Verifica si puede leer empresas"""
    return has_permission(role_name, Permission.COMPANY_MANAGEMENT, Action.READ)


def can_write_companies(role_name: str) -> bool:
    """Verifica si puede crear/editar empresas"""
    return has_permission(role_name, Permission.COMPANY_MANAGEMENT, Action.WRITE)


def can_delete_companies(role_name: str) -> bool:
    """Verifica si puede eliminar empresas"""
    return has_permission(role_name, Permission.COMPANY_MANAGEMENT, Action.DELETE)


def can_read_reports(role_name: str) -> bool:
    """Verifica si puede leer reportes"""
    return has_permission(role_name, Permission.REPORTS_ANALYTICS, Action.READ)


def can_export_reports(role_name: str) -> bool:
    """Verifica si puede exportar reportes"""
    return has_permission(role_name, Permission.REPORTS_ANALYTICS, Action.EXPORT)


def can_read_logs(role_name: str) -> bool:
    """Verifica si puede leer logs del sistema"""
    return has_permission(role_name, Permission.SYSTEM_LOGS, Action.READ)


def can_audit_logs(role_name: str) -> bool:
    """Verifica si puede auditar logs del sistema"""
    return has_permission(role_name, Permission.SYSTEM_LOGS, Action.AUDIT)
