from contextlib import contextmanager

from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy


class SQLAlchemy(_SQLAlchemy):
  """重写flask_sqlalchemy中的核心类，实现自动提交"""

  @contextmanager
  def auto_commit(self):
    try:
      yield
      self.session.commit()
    except Exception:
      self.session.rollback()
      raise
