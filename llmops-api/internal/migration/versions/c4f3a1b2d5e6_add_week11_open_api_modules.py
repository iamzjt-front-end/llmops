"""Add app configuration, API key, and open API end-user tables.

Revision ID: c4f3a1b2d5e6
Revises: b91e26a4c803
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = 'c4f3a1b2d5e6'
down_revision = 'b91e26a4c803'
branch_labels = None
depends_on = None


def _timestamps():
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


def _config_columns(include_version=False):
  columns = [
    sa.Column(
      'id', sa.UUID(), nullable=False, server_default=sa.text('uuid_generate_v4()')
    ),
    sa.Column('app_id', sa.UUID(), nullable=False),
    sa.Column(
      'model_config',
      postgresql.JSONB(),
      nullable=False,
      server_default=sa.text("'{}'::jsonb"),
    ),
    sa.Column(
      'dialog_round', sa.Integer(), nullable=False, server_default=sa.text('0')
    ),
    sa.Column(
      'preset_prompt', sa.Text(), nullable=False, server_default=sa.text("''::text")
    ),
    sa.Column(
      'tools', postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")
    ),
    sa.Column(
      'workflows',
      postgresql.JSONB(),
      nullable=False,
      server_default=sa.text("'[]'::jsonb"),
    ),
  ]
  if include_version:
    columns.append(
      sa.Column(
        'datasets',
        postgresql.JSONB(),
        nullable=False,
        server_default=sa.text("'[]'::jsonb"),
      )
    )
  columns.extend(
    [
      sa.Column(
        'retrieval_config',
        postgresql.JSONB(),
        nullable=False,
        server_default=sa.text("'{}'::jsonb"),
      ),
      sa.Column(
        'long_term_memory',
        postgresql.JSONB(),
        nullable=False,
        server_default=sa.text("'{}'::jsonb"),
      ),
      sa.Column(
        'opening_statement',
        sa.Text(),
        nullable=False,
        server_default=sa.text("''::text"),
      ),
      sa.Column(
        'opening_questions',
        postgresql.JSONB(),
        nullable=False,
        server_default=sa.text("'[]'::jsonb"),
      ),
      sa.Column(
        'speech_to_text',
        postgresql.JSONB(),
        nullable=False,
        server_default=sa.text("'{}'::jsonb"),
      ),
      sa.Column(
        'text_to_speech',
        postgresql.JSONB(),
        nullable=False,
        server_default=sa.text("'{}'::jsonb"),
      ),
      sa.Column(
        'suggested_after_answer',
        postgresql.JSONB(),
        nullable=False,
        server_default=sa.text('\'{"enable": true}\'::jsonb'),
      ),
      sa.Column(
        'review_config',
        postgresql.JSONB(),
        nullable=False,
        server_default=sa.text("'{}'::jsonb"),
      ),
    ]
  )
  if include_version:
    columns.extend(
      [
        sa.Column('version', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column(
          'config_type',
          sa.String(255),
          nullable=False,
          server_default=sa.text("''::character varying"),
        ),
      ]
    )
  columns.extend(_timestamps())
  return columns


def upgrade():
  op.create_table(
    'app_config',
    *_config_columns(),
    sa.PrimaryKeyConstraint('id', name='pk_app_config_id'),
  )
  op.create_table(
    'app_config_version',
    *_config_columns(include_version=True),
    sa.PrimaryKeyConstraint('id', name='pk_app_config_version_id'),
  )
  with op.batch_alter_table('app') as batch_op:
    batch_op.add_column(sa.Column('app_config_id', sa.UUID(), nullable=True))
    batch_op.add_column(sa.Column('draft_app_config_id', sa.UUID(), nullable=True))
    batch_op.add_column(sa.Column('debug_conversation_id', sa.UUID(), nullable=True))

  op.create_table(
    'api_key',
    sa.Column(
      'id', sa.UUID(), nullable=False, server_default=sa.text('uuid_generate_v4()')
    ),
    sa.Column('account_id', sa.UUID(), nullable=False),
    sa.Column(
      'api_key',
      sa.String(255),
      nullable=False,
      server_default=sa.text("''::character varying"),
    ),
    sa.Column(
      'is_active', sa.Boolean(), nullable=False, server_default=sa.text('false')
    ),
    sa.Column(
      'remark',
      sa.String(255),
      nullable=False,
      server_default=sa.text("''::character varying"),
    ),
    *_timestamps(),
    sa.PrimaryKeyConstraint('id', name='pk_api_key_id'),
  )
  op.create_table(
    'end_user',
    sa.Column(
      'id', sa.UUID(), nullable=False, server_default=sa.text('uuid_generate_v4()')
    ),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('app_id', sa.UUID(), nullable=False),
    *_timestamps(),
    sa.PrimaryKeyConstraint('id', name='pk_end_user_id'),
  )


def downgrade():
  op.drop_table('end_user')
  op.drop_table('api_key')
  with op.batch_alter_table('app') as batch_op:
    batch_op.drop_column('debug_conversation_id')
    batch_op.drop_column('draft_app_config_id')
    batch_op.drop_column('app_config_id')
  op.drop_table('app_config_version')
  op.drop_table('app_config')
