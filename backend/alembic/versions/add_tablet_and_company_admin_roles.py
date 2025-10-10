"""Add tablet and company admin roles

Revision ID: tablet_company_admin_001
Revises: f384ebd46d5c
Create Date: 2025-10-10 14:30:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = "tablet_company_admin_001"
down_revision = "f384ebd46d5c"
branch_labels = None
depends_on = None


def upgrade():
    """Add new roles: tablet and company_admin"""

    # Create refresh_tokens table if it doesn't exist
    try:
        op.create_table(
            "refresh_tokens",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("token", sa.String(255), nullable=False),
            sa.Column("expires_at", sa.DateTime(), nullable=False),
            sa.Column("is_revoked", sa.Boolean(), default=False),
            sa.Column("created_at", sa.DateTime(), default=sa.func.now()),
            sa.Column("last_used", sa.DateTime(), nullable=True),
            sa.Column("device_info", sa.String(500), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.Index("ix_refresh_tokens_token", "token"),
        )
    except Exception:
        # Table might already exist, continue with role creation
        pass

    # Insert tablet role
    op.execute(
        text("""
        INSERT INTO roles (name, description, permissions, scope, created_at) 
        VALUES (
            'tablet',
            'Tablet device role with employee management and time tracking capabilities',
            JSON_OBJECT(
                'employees_management', JSON_ARRAY('create', 'read', 'update'),
                'time_tracking', JSON_ARRAY('create', 'read'),
                'logs_audit', JSON_ARRAY('read'),
                'face_recognition', JSON_ARRAY('create', 'read')
            ),
            'warehouse',
            NOW()
        )
    """)
    )

    # Insert company_admin role
    op.execute(
        text("""
        INSERT INTO roles (name, description, permissions, scope, created_at)
        VALUES (
            'company_admin',
            'Company administrator with full permissions within their company',
            JSON_OBJECT(
                'company_management', JSON_ARRAY('create', 'read', 'update', 'delete'),
                'warehouses_management', JSON_ARRAY('create', 'read', 'update', 'delete'),
                'employees_management', JSON_ARRAY('create', 'read', 'update', 'delete'),
                'users_management', JSON_ARRAY('create', 'read', 'update', 'delete'),
                'roles_management', JSON_ARRAY('read'),
                'time_tracking', JSON_ARRAY('create', 'read', 'update', 'delete'),
                'logs_audit', JSON_ARRAY('read'),
                'reports_analytics', JSON_ARRAY('read'),
                'dashboard_read', JSON_ARRAY('read'),
                'face_recognition', JSON_ARRAY('create', 'read', 'update', 'delete')
            ),
            'company',
            NOW()
        )
    """)
    )


def downgrade():
    """Remove tablet and company_admin roles and refresh_tokens table"""

    # Remove the new roles
    op.execute(text("DELETE FROM roles WHERE name IN ('tablet', 'company_admin')"))

    # Drop refresh_tokens table
    op.drop_table("refresh_tokens")
