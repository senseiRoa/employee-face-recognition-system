from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from schemas import RoleWithPermissions, PermissionDetail
from services import role_service
from dependencies import get_current_user
from utils.permissions import get_role_permissions
from models import User

router = APIRouter()


@router.get("/", response_model=List[RoleWithPermissions])
def list_roles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all roles with their permission details for frontend configuration
    """
    # Obtener roles de la base de datos
    roles = role_service.get_roles(db, skip=skip, limit=limit)
    
    # Construir respuesta con permisos
    roles_with_permissions = []
    
    for role in roles:
        # Obtener permisos del enum ROLE_PERMISSIONS
        role_perms = get_role_permissions(role.name)
        
        # Convertir a formato PermissionDetail
        permissions = []
        for perm_set in role_perms:
            permission_detail = PermissionDetail(
                permission=perm_set.permission.value,
                actions=[action.value for action in perm_set.actions]
            )
            permissions.append(permission_detail)
        
        # Crear objeto RoleWithPermissions
        role_with_perms = RoleWithPermissions(
            id=role.id,
            name=role.name,
            description=role.description,
            created_at=role.created_at,
            permissions=permissions
        )
        roles_with_permissions.append(role_with_perms)
    
    return roles_with_permissions
