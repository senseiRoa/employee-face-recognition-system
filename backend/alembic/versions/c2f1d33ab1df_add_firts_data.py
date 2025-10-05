"""add firts data

Revision ID: c2f1d33ab1df
Revises: 6cbda2a442df
Create Date: 2025-10-05 03:17:57.967315

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer, DateTime, Boolean
import datetime


# revision identifiers, used by Alembic.
revision: str = "c2f1d33ab1df"
down_revision: Union[str, Sequence[str], None] = "6cbda2a442df"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create initial data
    create_initial_data()


def downgrade() -> None:
    """Downgrade schema."""
    pass


def create_initial_data():
    """Create initial roles, demo company, warehouse, and admin user with warehouse-based architecture"""
    connection = op.get_bind()

    # Check if roles already exist
    roles_exist = connection.execute(sa.text("SELECT COUNT(*) FROM roles")).scalar()

    if roles_exist == 0:
        # Define the tables for data insertion
        roles_table = table(
            "roles",
            column("name", String),
            column("description", String),
            column("permissions", sa.JSON),
            column("scope", String),
            column("created_at", DateTime),
        )

        # Insert roles with warehouse-based permissions
        op.bulk_insert(
            roles_table,
            [
                {
                    "name": "admin",
                    "description": "System administrator with full access",
                    "permissions": '{"can_manage_users": true, "can_manage_employees": true, "can_view_reports": true, "can_manage_warehouses": true, "can_manage_companies": true}',
                    "scope": "warehouse",
                    "created_at": datetime.datetime.utcnow(),
                },
                {
                    "name": "manager",
                    "description": "Warehouse manager with access to their warehouse",
                    "permissions": '{"can_manage_employees": true, "can_view_reports": true, "can_manage_access": true, "can_manage_warehouse_settings": true}',
                    "scope": "warehouse",
                    "created_at": datetime.datetime.utcnow(),
                },
                {
                    "name": "employee",
                    "description": "Employee with basic access",
                    "permissions": '{"can_clock_in": true, "can_view_own_logs": true, "can_view_own_profile": true}',
                    "scope": "warehouse",
                    "created_at": datetime.datetime.utcnow(),
                },
            ],
        )

    # Check if demo company already exists
    companies_exist = connection.execute(
        sa.text("SELECT COUNT(*) FROM companies WHERE name = 'Demo Company'")
    ).scalar()

    if companies_exist == 0:
        companies_table = table(
            "companies",
            column("name", String),
            column("email", String),
            column("phone", String),
            column("address", String),
            column("created_at", DateTime),
        )

        # Insert demo company
        op.bulk_insert(
            companies_table,
            [
                {
                    "name": "Demo Company",
                    "email": "info@democompany.com",
                    "phone": "+1-555-0123",
                    "address": "123 Demo Street, Demo City, DC 12345",
                    "created_at": datetime.datetime.utcnow(),
                }
            ],
        )

    # Check if demo warehouse already exists
    warehouses_exist = connection.execute(
        sa.text("SELECT COUNT(*) FROM warehouses WHERE name = 'Main Warehouse'")
    ).scalar()

    if warehouses_exist == 0:
        # Get demo company ID
        company_id = connection.execute(
            sa.text("SELECT id FROM companies WHERE name = 'Demo Company'")
        ).scalar()

        if company_id:
            warehouses_table = table(
                "warehouses",
                column("company_id", Integer),
                column("name", String),
                column("location", String),
                column("timezone", String),
                column("is_active", Boolean),
                column("created_at", DateTime),
            )

            # Insert demo warehouse
            op.bulk_insert(
                warehouses_table,
                [
                    {
                        "company_id": company_id,
                        "name": "Main Warehouse",
                        "location": "123 Demo Street, Demo City, DC 12345",
                        "timezone": "America/New_York",
                        "is_active": True,
                        "created_at": datetime.datetime.utcnow(),
                    }
                ],
            )

    # Check if admin user already exists
    admin_exists = connection.execute(
        sa.text("SELECT COUNT(*) FROM users WHERE username = 'admin'")
    ).scalar()

    if admin_exists == 0:
        # Get IDs for admin role and demo warehouse
        admin_role_id = connection.execute(
            sa.text("SELECT id FROM roles WHERE name = 'admin'")
        ).scalar()
        warehouse_id = connection.execute(
            sa.text("SELECT id FROM warehouses WHERE name = 'Main Warehouse'")
        ).scalar()

        if admin_role_id and warehouse_id:
            users_table = table(
                "users",
                column("warehouse_id", Integer),
                column("role_id", Integer),
                column("username", String),
                column("email", String),
                column("password", String),
                column("first_name", String),
                column("last_name", String),
                column("is_active", Boolean),
                column("created_at", DateTime),
                column("password_changed_at", DateTime),
            )

            # Insert admin user (password: Admin123! - bcrypt hash)
            op.bulk_insert(
                users_table,
                [
                    {
                        "warehouse_id": warehouse_id,
                        "role_id": admin_role_id,
                        "username": "admin",
                        "email": "admin@democompany.com",
                        "password": "$2b$12$bNQ3Euxn1FEqwZ4ZWSCQcO04hVunfo9EPPNLUyOIIdx1d0Un55iTG",  # Admin123!
                        "first_name": "Admin",
                        "last_name": "User",
                        "is_active": True,
                        "created_at": datetime.datetime.utcnow(),
                        "password_changed_at": datetime.datetime.utcnow(),
                    }
                ],
            )
