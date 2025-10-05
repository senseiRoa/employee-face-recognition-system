"""
Script para crear usuarios iniciales con contraseñas fuertes
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import sessionmaker
from database import engine, get_db
from models import User, Role, Company
from utils.security import get_password_hash
from utils.generate_test_passwords import get_test_passwords
import datetime


def create_initial_users():
    """Crear usuarios iniciales con contraseñas fuertes"""

    # Crear session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Verificar si ya existen usuarios
        existing_users = db.query(User).first()
        if existing_users:
            print("⚠️ Users already exist in database. Skipping creation.")
            return

        passwords = get_test_passwords()

        # Crear company si no existe
        company = db.query(Company).first()
        if not company:
            company = Company(
                id=1,
                name="Demo Company",
                email="demo@company.com",
                phone="555-0123",
                address="123 Demo Street",
            )
            db.add(company)
            db.commit()
            db.refresh(company)

        # Crear roles si no existen
        roles_data = [
            {"id": 1, "name": "admin", "description": "System Administrator"},
            {"id": 2, "name": "manager", "description": "Company Manager"},
            {"id": 3, "name": "employee", "description": "Regular Employee"},
        ]

        for role_data in roles_data:
            existing_role = (
                db.query(Role).filter(Role.name == role_data["name"]).first()
            )
            if not existing_role:
                role = Role(**role_data)
                db.add(role)

        db.commit()

        # Crear usuarios con contraseñas fuertes
        users_data = [
            {
                "id": 1,
                "username": "admin",
                "email": "admin@demo.com",
                "password": get_password_hash(passwords["admin"]),
                "first_name": "System",
                "last_name": "Administrator",
                "role_id": 1,
                "company_id": 1,
            },
            {
                "id": 2,
                "username": "manager",
                "email": "manager@demo.com",
                "password": get_password_hash(passwords["manager"]),
                "first_name": "Demo",
                "last_name": "Manager",
                "role_id": 2,
                "company_id": 1,
            },
            {
                "id": 3,
                "username": "employee",
                "email": "employee@demo.com",
                "password": get_password_hash(passwords["employee"]),
                "first_name": "Demo",
                "last_name": "Employee",
                "role_id": 3,
                "company_id": 1,
            },
        ]

        for user_data in users_data:
            user = User(
                **user_data,
                is_active=True,
                created_at=datetime.datetime.utcnow(),
                password_changed_at=datetime.datetime.utcnow(),
            )
            db.add(user)

        db.commit()

        print("✅ Successfully created initial users with strong passwords:")
        print(f"   Admin: admin / {passwords['admin']}")
        print(f"   Manager: manager / {passwords['manager']}")
        print(f"   Employee: employee / {passwords['employee']}")

    except Exception as e:
        db.rollback()
        print(f"❌ Error creating users: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🔐 Creating initial users with strong passwords...")
    create_initial_users()
    print("🎉 Done!")
