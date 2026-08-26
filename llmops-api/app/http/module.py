from flask_sqlalchemy import SQLAlchemy
from injector import Binder, Module

from internal.extension import db


class ExtensionModule(Module):
  """扩展模块的依赖注入"""

  def configure(self, binder: Binder) -> None:
    binder.bind(SQLAlchemy, to=db)
