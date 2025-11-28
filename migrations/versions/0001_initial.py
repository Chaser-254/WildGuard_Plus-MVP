"""initial migration

Revision ID: 0001_initial
Revises: 
Create Date: 2025-11-26
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
deploy_revision = None


def upgrade():
    # Create camera table
    op.create_table(
        'camera',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('camera_id', sa.String(length=50), nullable=False, unique=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.sql.expression.false()),
        sa.Column('last_seen', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    # Create subscriber table
    op.create_table(
        'subscriber',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.sql.expression.true()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    # Create detections table
    op.create_table(
        'detections',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('species', sa.String(length=50), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('image_path', sa.String(length=200), nullable=True),
        sa.Column('is_verified', sa.Boolean(), server_default=sa.sql.expression.false()),
        sa.Column('is_false_positive', sa.Boolean(), server_default=sa.sql.expression.false()),
    )


def downgrade():
    op.drop_table('detections')
    op.drop_table('subscriber')
    op.drop_table('camera')
