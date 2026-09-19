import pytest

from internal.model import Account
from internal.service import AppService, JwtService
from pkg.response import HttpCode

ACCOUNT_ID = '46db30d1-3199-4e79-a0cd-abf12fa6858f'


@pytest.fixture(autouse=True)
def authenticated_client(db, client, monkeypatch):
  monkeypatch.setenv('JWT_SECRET_KEY', 'test-jwt-secret-at-least-32-bytes')
  db.session.add(
    Account(
      id=ACCOUNT_ID,
      name='测试账号',
      email='test@example.com',
      avatar='',
      last_login_ip='127.0.0.1',
    )
  )
  db.session.flush()
  token = JwtService.generate_token({'sub': ACCOUNT_ID})
  client.environ_base['HTTP_AUTHORIZATION'] = f'Bearer {token}'


class TestAppHandler:
  """app控制器的测试类"""

  @pytest.mark.parametrize(
    'app_id, query',
    [
      ('3d105834-a524-4996-be14-648670fd8291', None),
      ('3d105834-a524-4996-be14-648670fd8291', '你好，你是？'),
    ],
  )
  def test_completion(self, app_id, query, client, monkeypatch):
    monkeypatch.setattr(
      AppService,
      'debug_chat',
      lambda self, app_id, query, account: iter(
        ['event: agent_message\ndata:{"answer":"你好"}\n\n']
      ),
    )
    resp = client.post(f'/apps/{app_id}/debug', json={'query': query})
    assert resp.status_code == 200
    if query is None:
      assert resp.json.get('code') == HttpCode.VALIDATE_ERROR
    else:
      assert resp.mimetype == 'text/event-stream'
      assert '"answer":"你好"' in resp.get_data(as_text=True)
