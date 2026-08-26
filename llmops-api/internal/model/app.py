import uuid
from datetime import datetime

from sqlalchemy import UUID, Column, DateTime, Index, PrimaryKeyConstraint, String, Text

from internal.extension.database_extension import db


class App(db.Model):
  """AI基础运用模型类"""

  __tablename__ = 'app'
  __table_args__ = (
    PrimaryKeyConstraint('id', name='pk_app_id'),
    Index('idx_app_account_id', 'account_id'),
  )

  id = Column(UUID, default=uuid.uuid4, nullable=False)
  account_id = Column(UUID, nullable=False)
  name = Column(String(255), default='', nullable=False)
  icon = Column(String(255), default='', nullable=False)
  description = Column(Text, default='', nullable=False)
  update_time = Column(
    DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
  )
  create_time = Column(
    DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
  )
