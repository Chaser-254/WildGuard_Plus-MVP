"""add camera_id to detections

Revision ID: 0002_add_camera_id
Revises: 0001_initial
Create Date: 2025-11-28
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0002_add_camera_id'
down_revision = '0001_initial'
branch_labels = None
deploy_revision = None


def upgrade():
    # Add a nullable camera_id column to detections
    op.add_column('detections', sa.Column('camera_id', sa.String(length=50), nullable=True))


def downgrade():
    # Remove the camera_id column
    op.drop_column('detections', 'camera_id')
