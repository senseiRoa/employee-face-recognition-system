"""
Script para migrar y actualizar permisos de roles en la base de datos
Ejecutar con: python scripts/migrate_permissions.py
"""

import sys
import os

# Agregar el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Role
from utils.permissions import get_permissions_json, ROLE_PERMISSIONS


def migrate_role_permissions():
    """
    Migra los permisos de los roles a la base de datos
    """
    db: Session = SessionLocal()

    try:
        print("🔄 Iniciando migración de permisos de roles...")

        # Verificar que existen los 3 roles requeridos
        required_roles = ["admin", "manager", "employee"]
        existing_roles = db.query(Role).filter(Role.name.in_(required_roles)).all()
        existing_role_names = [role.name for role in existing_roles]

        print(f"📋 Roles encontrados en BD: {existing_role_names}")

        # Crear roles faltantes si es necesario
        for role_name in required_roles:
            if role_name not in existing_role_names:
                print(f"➕ Creando rol faltante: {role_name}")

                # Definir descripciones de roles
                descriptions = {
                    "admin": "System administrator with full access",
                    "manager": "Warehouse manager with access to their warehouse",
                    "employee": "Employee with basic access only read",
                }

                new_role = Role(
                    name=role_name,
                    description=descriptions[role_name],
                    permissions=get_permissions_json(role_name),
                    scope="warehouse",
                )
                db.add(new_role)

        # Actualizar permisos de roles existentes
        print("🔧 Actualizando permisos de roles existentes...")

        for role in existing_roles:
            if role.name in ROLE_PERMISSIONS:
                old_permissions = role.permissions
                new_permissions = get_permissions_json(role.name)

                print(f"📝 Actualizando permisos para rol: {role.name}")
                print(f"   Permisos anteriores: {old_permissions}")
                print(f"   Permisos nuevos: {new_permissions}")

                role.permissions = new_permissions

                # Actualizar descripción también
                descriptions = {
                    "admin": "System administrator with full access",
                    "manager": "Warehouse manager with access to their warehouse",
                    "employee": "Employee with basic access only read",
                }
                role.description = descriptions.get(role.name, role.description)

        # Guardar cambios
        db.commit()
        print("✅ Migración completada exitosamente!")

        # Mostrar resumen final
        print("\n📊 RESUMEN DE PERMISOS POR ROL:")
        print("=" * 50)

        updated_roles = db.query(Role).filter(Role.name.in_(required_roles)).all()
        for role in updated_roles:
            print(f"\n🔑 {role.name.upper()}:")
            print(f"   Descripción: {role.description}")
            print(f"   Permisos: {role.permissions}")

    except Exception as e:
        print(f"❌ Error durante la migración: {str(e)}")
        db.rollback()
        raise

    finally:
        db.close()


def validate_permissions():
    """
    Valida que los permisos se aplicaron correctamente
    """
    db: Session = SessionLocal()

    try:
        print("\n🔍 Validando permisos aplicados...")

        roles = (
            db.query(Role).filter(Role.name.in_(["admin", "manager", "employee"])).all()
        )

        validation_passed = True

        for role in roles:
            expected_permissions = get_permissions_json(role.name)
            actual_permissions = role.permissions

            if actual_permissions != expected_permissions:
                print(f"❌ Error en permisos del rol {role.name}")
                print(f"   Esperado: {expected_permissions}")
                print(f"   Actual: {actual_permissions}")
                validation_passed = False
            else:
                print(f"✅ Permisos correctos para rol: {role.name}")

        if validation_passed:
            print("\n🎉 Todos los permisos están correctamente aplicados!")
        else:
            print("\n❌ Hay errores en los permisos aplicados!")
            return False

        return True

    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 MIGRACIÓN DE PERMISOS DE ROLES")
    print("=" * 40)

    try:
        # Ejecutar migración
        migrate_role_permissions()

        # Validar resultados
        if validate_permissions():
            print("\n✨ Migración completada con éxito!")
            sys.exit(0)
        else:
            print("\n💥 Migración falló en la validación!")
            sys.exit(1)

    except Exception as e:
        print(f"\n💥 Error crítico durante la migración: {str(e)}")
        sys.exit(1)
