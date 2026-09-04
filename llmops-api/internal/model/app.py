import uuid

from sqlalchemy import (
  UUID,
  Column,
  DateTime,
  Index,
  PrimaryKeyConstraint,
  String,
  Text,
  text,
)

from internal.extension.database_extension import db


class App(db.Model):
  """AI基础运用模型类"""

  __tablename__ = 'app'
  __table_args__ = (
    PrimaryKeyConstraint('id', name='pk_app_id'),
    Index('idx_app_account_id', 'account_id'),
  )

  id = Column(
    UUID, default=uuid.uuid4, nullable=False, server_default=text('uuid_generate_v4()')
  )
  account_id = Column(UUID)
  name = Column(
    String(255), nullable=False, server_default=text("''::character varying")
  )
  icon = Column(
    String(255), nullable=False, server_default=text("''::character varying")
  )
  description = Column(Text, nullable=False, server_default=text("''::text"))
  status = Column(
    String(255), nullable=False, server_default=text("''::character varying")
  )
  update_at = Column(
    DateTime,
    nullable=False,
    server_default=text('CURRENT_TIMESTAMP(0)'),
    server_onupdate=text('CURRENT_TIMESTAMP(0)'),
  )
  create_at = Column(
    DateTime,
    nullable=False,
    server_default=text('CURRENT_TIMESTAMP(0)'),
    server_onupdate=text('CURRENT_TIMESTAMP(0)'),
  )
