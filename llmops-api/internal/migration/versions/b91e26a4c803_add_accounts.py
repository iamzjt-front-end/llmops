"""Register the account models already present in week 8 chapter 1.

Revision ID: b91e26a4c803
Revises: 5053763c94fe
"""

import sqlalchemy as sa
from alembic import op

revision = 'b91e26a4c803'
down_revision = '5053763c94fe'
branch_labels = None
depends_on = None


def timestamps():
  return [
    sa.Column(
      'updated_at',
      sa.DateTime(),
      nullable=False,
      server_default=sa.text('CURRENT_TIMESTAMP(0)'),
    ),
    sa.Column(
      'created_at',
      sa.DateTime(),
      nullable=False,
      server_default=sa.text('CURRENT_TIMESTAMP(0)'),
    ),
  ]


def upgrade():
  op.create_table(
    'account',
    sa.Column(
      'id', sa.UUID(), nullable=False, server_default=sa.text('uuid_generate_v4()')
    ),
    *[
      sa.Column(name, sa.String(255), nullable=False, server_default='')
      for name in ['name', 'email', 'avatar', 'last_login_ip']
    ],
    *[
      sa.Column(name, sa.String(255), nullable=True, server_default='')
      for name in ['password', 'password_salt']
    ],
    sa.Column(
      'last_login_at',
      sa.DateTime(),
      nullable=False,
      server_default=sa.text('CURRENT_TIMESTAMP(0)'),
    ),
    *timestamps(),
    sa.PrimaryKeyConstraint('id', name='pk_account_id'),
  )
  op.create_table(
    'account_oauth',
    sa.Column(
      'id', sa.UUID(), nullable=False, server_default=sa.text('uuid_generate_v4()')
    ),
    sa.Column('account_id', sa.UUID(), nullable=False),
    *[
      sa.Column(name, sa.String(255), nullable=False, server_default='')
      for name in ['provider', 'openid']
    ],
    sa.Column('encrypted_token', sa.String(255), nullable=False),
    *timestamps(),
    sa.PrimaryKeyConstraint('id', name='pk_account_oauth_id'),
  )


def downgrade():
  op.drop_table('account_oauth')
  op.drop_table('account')
