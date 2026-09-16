import pytest
from sqlalchemy.orm import scoped_session, sessionmaker

from app.http.app import app as _app
from internal.extension.database_extension import db as _db


@pytest.fixture
def app():
  """获取 Flask 测试应用。"""
  _app.config['TESTING'] = True
  return _app


@pytest.fixture
def client(app):
  """获取Flask应用的测试应用, 并返回"""
  with app.test_client() as client:
    yield client


@pytest.fixture
def db(app):
  """使用独立事务运行数据库测试，用例结束后统一回滚。"""
  with app.app_context():
    connection = _db.engine.connect()
    transaction = connection.begin()
    original_session = _db.session
    test_session = scoped_session(sessionmaker(bind=connection))
    _db.session = test_session

    try:
      yield _db
    finally:
      test_session.remove()
      _db.session = original_session
      transaction.rollback()
      connection.close()
