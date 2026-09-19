from flask_login import LoginManager
from flask_migrate import Migrate
from injector import Binder, Injector, Module
from redis import Redis

from internal.extension import db, migrate
from internal.extension.login_extension import login_manager
from internal.extension.redis_extension import redis_client
from pkg.sqlalchemy import SQLAlchemy


class ExtensionModule(Module):
  """扩展模块的依赖注入"""

  def configure(self, binder: Binder) -> None:
    binder.bind(SQLAlchemy, to=db)
    binder.bind(Migrate, to=migrate)
    binder.bind(LoginManager, to=login_manager)
    binder.bind(Redis, to=redis_client)


injector = Injector([ExtensionModule])
