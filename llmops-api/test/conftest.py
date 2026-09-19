import uuid
from pathlib import Path

import pytest
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.operations import Operations
from alembic.script import ScriptDirectory
from sqlalchemy import text
from sqlalchemy.orm import scoped_session, sessionmaker

from app.http.app import app as _app
from internal.extension.database_extension import db as _db


@pytest.fixture
def app():
  _app.config['TESTING'] = True
  return _app


@pytest.fixture
def client(app):
  with app.test_client() as client:
    yield client


@pytest.fixture
def db(app):
  """迁移和测试均在独立 schema + 外层事务内运行，结束后整体回滚。"""
  with app.app_context():
    connection = _db.engine.connect()
    transaction = connection.begin()
    original_session = _db.session
    schema = f'llmops_test_{uuid.uuid4().hex}'
    try:
      connection.execute(text(f'CREATE SCHEMA "{schema}"'))
      connection.execute(text(f'SET LOCAL search_path TO "{schema}", public'))
      config = Config()
      config.set_main_option(
        'script_location',
        str(Path(__file__).resolve().parents[1] / 'internal/migration'),
      )
      scripts = ScriptDirectory.from_config(config)
      context = MigrationContext.configure(connection)
      with Operations.context(context):
        for revision in reversed(list(scripts.walk_revisions())):
          revision.module.upgrade()
      test_session = scoped_session(
        sessionmaker(bind=connection, join_transaction_mode='create_savepoint')
      )
      _db.session = test_session
      yield _db
    finally:
      if _db.session is not original_session:
        _db.session.remove()
      _db.session = original_session
      transaction.rollback()
      connection.close()
