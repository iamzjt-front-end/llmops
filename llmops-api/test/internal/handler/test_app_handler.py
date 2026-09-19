import pytest
from langchain_core.language_models.fake_chat_models import FakeListChatModel

from internal.handler.app_handler import AppHandler
from pkg.response import HttpCode


class TestAppHandler:
  """app控制器的测试类"""

  @pytest.mark.parametrize(
    'app_id, query',
    [
      ('3d105834-a524-4996-be14-648670fd8291', None),
      ('3d105834-a524-4996-be14-648670fd8291', '你好，你是？'),
    ],
  )
  def test_completion(self, app_id, query, client, monkeypatch, tmp_path):
    from internal.lib.chat_history import FileChatMessageHistory

    monkeypatch.setattr(
      AppHandler,
      '_get_llm',
      staticmethod(lambda: FakeListChatModel(responses=['你好'])),
    )
    monkeypatch.setattr(
      AppHandler,
      '_get_chat_history',
      staticmethod(
        lambda app_id: FileChatMessageHistory(str(tmp_path / 'history.json'))
      ),
    )
    resp = client.post(f'/apps/{app_id}/debug', json={'query': query})
    assert resp.status_code == 200
    if query is None:
      assert resp.json.get('code') == HttpCode.VALIDATE_ERROR
    else:
      assert resp.json.get('code') == HttpCode.SUCCESS
    print('响应内容：', resp.json)
