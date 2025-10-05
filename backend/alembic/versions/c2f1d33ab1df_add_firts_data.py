"""add firts data

Revision ID: c2f1d33ab1df
Revises: 6cbda2a442df
Create Date: 2025-10-05 03:17:57.967315

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
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
    """Create initial roles, demo company, and admin user"""
    connection = op.get_bind()

    # Check if roles already exist
    roles_exist = connection.execute(sa.text("SELECT COUNT(*) FROM roles")).scalar()

    if roles_exist == 0:
        # Define the tables for data insertion
        roles_table = table(
            "roles",
            column("name", String),
            column("description", String),
            column("created_at", DateTime),
        )

        # Insert roles
        op.bulk_insert(
            roles_table,
            [
                {
                    "name": "admin",
                    "description": "System administrator with full access",
                    "created_at": datetime.datetime.utcnow(),
                },
                {
                    "name": "manager",
                    "description": "Company manager with access to their company",
                    "created_at": datetime.datetime.utcnow(),
                },
                {
                    "name": "employee",
                    "description": "Employee with basic access",
                    "created_at": datetime.datetime.utcnow(),
                },
            ],
        )

    # Check if demo company already exists
    companies_exist = connection.execute(
        sa.text("SELECT COUNT(*) FROM companies WHERE name = 'Admin Company'")
    ).scalar()

    if companies_exist == 0:
        companies_table = table(
            "companies",
            column("name", String),
            column("email", String),
            column("created_at", DateTime),
        )

        # Insert demo company
        op.bulk_insert(
            companies_table,
            [
                {
                    "name": "Admin Company",
                    "email": "admin@admincompany.com",
                    "created_at": datetime.datetime.utcnow(),
                }
            ],
        )

    # Check if admin user already exists
    admin_exists = connection.execute(
        sa.text("SELECT COUNT(*) FROM users WHERE username = 'admin'")
    ).scalar()

    if admin_exists == 0:
        # Get IDs for admin role and demo company
        admin_role_id = connection.execute(
            sa.text("SELECT id FROM roles WHERE name = 'admin'")
        ).scalar()
        admin_company_id = connection.execute(
            sa.text("SELECT id FROM companies WHERE name = 'Admin Company'")
        ).scalar()

        if admin_role_id and admin_company_id:
            users_table = table(
                "users",
                column("company_id", Integer),
                column("role_id", Integer),
                column("username", String),
                column("email", String),
                column("password", String),
                column("first_name", String),
                column("last_name", String),
                column("is_active", Boolean),
                column("created_at", DateTime),
            )

            # Insert admin user (password: admin123 - bcrypt hash)
            op.bulk_insert(
                users_table,
                [
                    {
                        "company_id": admin_company_id,
                        "role_id": admin_role_id,
                        "username": "admin",
                        "email": "admin@democompany.com",
                        "password": "$2b$12$gR9TtVI/BfoiWxx1CQXFc.k9V8B9AanVu6dta8ruYSkwRaV0kQQoG",  # admin123
                        "first_name": "Admin",
                        "last_name": "User",
                        "is_active": True,
                        "created_at": datetime.datetime.utcnow(),
                    }
                ],
            )
