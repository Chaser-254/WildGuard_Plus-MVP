"""placeholder for missing revision 02b01a8eda20

This empty migration satisfies Alembic's lookup when a revision id
is referenced but the original migration file is missing. It's intended
for local/dev restoration only.

Revision ID: 02b01a8eda20
Revises: 0001_initial
Create Date: 2025-11-28
"""
from alembic import op
import sqlalchemy as sa

revision = '02b01a8eda20'
down_revision = '0001_initial'
branch_labels = None
deploy_revision = None


def upgrade():
    # Intentionally empty placeholder migration
    pass


def downgrade():
    # Nothing to revert
    pass
