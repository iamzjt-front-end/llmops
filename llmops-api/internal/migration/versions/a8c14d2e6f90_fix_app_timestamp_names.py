"""fix app timestamp column names

Revision ID: a8c14d2e6f90
Revises: e7dd573ebb72
Create Date: 2026-09-16 19:04:00

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = 'a8c14d2e6f90'
down_revision = 'e7dd573ebb72'
branch_labels = None
depends_on = None


def upgrade():
  op.alter_column('app', 'update_at', new_column_name='updated_at')
  op.alter_column('app', 'create_at', new_column_name='created_at')


def downgrade():
  op.alter_column('app', 'created_at', new_column_name='create_at')
  op.alter_column('app', 'updated_at', new_column_name='update_at')
