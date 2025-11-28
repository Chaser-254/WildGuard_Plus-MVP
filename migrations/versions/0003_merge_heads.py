"""merge heads

Revision ID: 0003_merge_heads
Revises: 0002_add_camera_id, 02b01a8eda20
Create Date: 2025-11-28
"""
from alembic import op
import sqlalchemy as sa

revision = '0003_merge_heads'
# multiple down revisions to merge divergent heads
down_revision = ('0002_add_camera_id', '02b01a8eda20')
branch_labels = None
deploy_revision = None


def upgrade():
    # Merge migration to unify heads. No DB changes required.
    pass


def downgrade():
    # Nothing to revert for merge
    pass
