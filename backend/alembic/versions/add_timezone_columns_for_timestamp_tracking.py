"""add timezone columns for timestamp tracking

Revision ID: add_timezone_cols
Revises: f384ebd46d5c
Create Date: 2025-10-08 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_timezone_cols'
down_revision: Union[str, Sequence[str], None] = 'f384ebd46d5c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add timezone columns to tables with timestamp fields to track 
    the device/client timezone when records are created.
    This ensures accurate reporting by preserving the original timezone context.
    """
    
    # Add timezone column to access_logs table
    # This tracks the device timezone when clock-in/clock-out events occur
    op.add_column('access_logs', sa.Column('device_timezone', sa.String(50), nullable=True, server_default='UTC'))
    
    # Add timezone column to user_login_logs table  
    # This tracks the client timezone when users log into the admin panel
    op.add_column('user_login_logs', sa.Column('client_timezone', sa.String(50), nullable=True, server_default='UTC'))
    
    # Add timezone column to companies table
    # This tracks the timezone when company records are created/updated
    op.add_column('companies', sa.Column('record_timezone', sa.String(50), nullable=True, server_default='UTC'))
    
    # Add timezone column to employees table
    # This tracks the timezone when employee records are created
    op.add_column('employees', sa.Column('record_timezone', sa.String(50), nullable=True, server_default='UTC'))
    
    # Add timezone column to users table
    # This tracks the timezone when user records are created
    op.add_column('users', sa.Column('record_timezone', sa.String(50), nullable=True, server_default='UTC'))
    
    # Add timezone column to face_encodings table
    # This tracks the timezone when face encodings are registered
    op.add_column('face_encodings', sa.Column('record_timezone', sa.String(50), nullable=True, server_default='UTC'))
    
    # Add timezone column to password_history table
    # This tracks the timezone when password changes occur
    op.add_column('password_history', sa.Column('record_timezone', sa.String(50), nullable=True, server_default='UTC'))


def downgrade() -> None:
    """
    Remove timezone columns from all tables.
    This will lose timezone information if executed.
    """
    
    # Remove timezone columns in reverse order
    op.drop_column('password_history', 'record_timezone')
    op.drop_column('face_encodings', 'record_timezone')
    op.drop_column('users', 'record_timezone')
    op.drop_column('employees', 'record_timezone')
    op.drop_column('companies', 'record_timezone')
    op.drop_column('user_login_logs', 'client_timezone')
    op.drop_column('access_logs', 'device_timezone')