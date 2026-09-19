import json
import uuid
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.messages import AIMessageChunk, HumanMessage
from langchain_core.tools import tool

from config import Config
from internal.core.agent.agents import AgentQueueManager, FunctionCallAgent
from internal.core.agent.entities.agent_entity import AgentConfig
from internal.core.agent.entities.queue_entity import QueueEvent
from internal.core.file_extractor import FileExtractor
from internal.entity.conversation_entity import InvokeFrom
from internal.entity.dataset_entity import DEFAULT_PROCESS_RULE
from internal.handler.app_handler import AppHandler
from internal.lib.chat_history import FileChatMessageHistory
from internal.schema.document_schema import CreateDocumentsReq
from internal.service import ProcessRuleService


def queue_manager():
  redis = Mock()
  redis.get.return_value = None
  return AgentQueueManager(uuid.uuid4(), uuid.uuid4(), InvokeFrom.DEBUGGER, redis)


def test_agent_stream_and_long_term_memory():
  manager = queue_manager()
  agent = FunctionCallAgent(
    AgentConfig(
      llm=FakeListChatModel(responses=['你好']), enable_long_term_memory=True
    ),
    manager,
  )
  events = list(agent.run('问候', [], '用户喜欢中文'))
  assert events[0].event == QueueEvent.LONG_TERM_MEMORY_RECALL
  assert events[0].observation == '用户喜欢中文'
  assert ''.join(event.answer for event in events) == '你好'
  assert events[-1].messages[0]['type'] == 'system'


def test_agent_background_exception_terminates_stream():
  agent = FunctionCallAgent(
    AgentConfig(llm=FakeListChatModel(responses=['unused'])), queue_manager()
  )
  events = list(agent.run('你好', [HumanMessage('不成对的历史')]))
  assert len(events) == 1
  assert events[0].event == QueueEvent.ERROR


def test_agent_tool_call_round_trip():
  @tool
  def add_one(number: int) -> int:
    """Add one to a number."""
    return number + 1

  class ToolModel(FakeListChatModel):
    def bind_tools(self, tools):
      return self

    def stream(self, messages, **kwargs):
      if messages[-1].type == 'tool':
        yield AIMessageChunk(content=messages[-1].content)
      else:
        yield AIMessageChunk(
          content='',
          tool_call_chunks=[
            {'name': 'add_one', 'args': '{"number": 2}', 'id': 'call-1', 'index': 0}
          ],
        )

  agent = FunctionCallAgent(
    AgentConfig(llm=ToolModel(responses=[]), tools=[add_one]), queue_manager()
  )
  events = list(agent.run('2 加 1'))
  assert [event.event for event in events] == [
    QueueEvent.AGENT_THOUGHT,
    QueueEvent.AGENT_ACTION,
    QueueEvent.AGENT_MESSAGE,
  ]
  assert events[1].tool_input == {'number': 2}
  assert events[-1].answer == '3'


def test_queue_timeout_and_stop():
  manager = queue_manager()
  assert list(manager.listen(timeout=0.01))[-1].event == QueueEvent.TIMEOUT
  manager = queue_manager()
  manager.redis_client.get.return_value = b'1'
  assert list(manager.listen(timeout=2))[-1].event == QueueEvent.STOP


def test_agent_sse_endpoint(client, monkeypatch, tmp_path):
  monkeypatch.setattr(
    AppHandler, '_get_llm', staticmethod(lambda: FakeListChatModel(responses=['你好']))
  )
  monkeypatch.setattr(
    AppHandler,
    '_get_chat_history',
    staticmethod(lambda _: FileChatMessageHistory(str(tmp_path / 'history.json'))),
  )
  for name in ['SERPER_API_KEY', 'GAODE_API_KEY', 'OPENAI_API_KEY']:
    monkeypatch.delenv(name, raising=False)
  from app.http.module import injector

  handler = injector.get(AppHandler)
  monkeypatch.setattr(handler.redis_client, 'setex', Mock())
  monkeypatch.setattr(handler.redis_client, 'get', Mock(return_value=None))
  response = client.post(
    f'/apps/{uuid.uuid4()}/debug',
    json={'query': '你好'},
    headers={'Accept': 'text/event-stream'},
  )
  assert response.mimetype == 'text/event-stream'
  events = [
    json.loads(line[6:])
    for line in response.get_data(as_text=True).splitlines()
    if line.startswith('data: ')
  ]
  assert ''.join(event['answer'] for event in events) == '你好'
  assert len(FileChatMessageHistory(str(tmp_path / 'history.json')).messages) == 2


@pytest.mark.parametrize(
  'extension, content, expected',
  [
    ('txt', '知识库测试', '知识库测试'),
    ('md', '# 标题\n知识库', '知识库'),
    ('csv', 'name,value\n知识库,1', '知识库\t1'),
    ('html', '<script>bad()</script><p>知识库</p>', '知识库'),
  ],
)
def test_extract_text_formats(tmp_path, extension, content, expected):
  path = tmp_path / f'test.{extension}'
  path.write_text(content)
  result = FileExtractor.load_from_file(str(path), return_text=True)
  assert expected in result
  assert 'bad()' not in result


def test_extract_office_and_pdf(tmp_path):
  from docx import Document
  from openpyxl import Workbook
  from pptx import Presentation
  from pypdf import PdfWriter

  document = Document()
  document.add_paragraph('知识库文档')
  document.save(tmp_path / 'test.docx')
  workbook = Workbook()
  workbook.active.append(['知识库表格', 1])
  workbook.save(tmp_path / 'test.xlsx')
  deck = Presentation()
  slide = deck.slides.add_slide(deck.slide_layouts[0])
  slide.shapes.title.text = '知识库幻灯片'
  deck.save(tmp_path / 'test.pptx')
  pdf = PdfWriter()
  pdf.add_blank_page(width=100, height=100)
  pdf.write(tmp_path / 'test.pdf')
  for extension in ['docx', 'xlsx', 'pptx']:
    assert '知识库' in FileExtractor.load_from_file(
      str(tmp_path / f'test.{extension}'), True
    )
  assert FileExtractor.load_from_file(str(tmp_path / 'test.pdf'), True) == ''


def test_process_rule_validation_and_splitting(app):
  with app.test_request_context(
    method='POST',
    json={'upload_file_ids': [str(uuid.uuid4())], 'process_type': 'automatic'},
  ):
    req = CreateDocumentsReq()
    assert req.validate(), req.errors
    assert req.rule.data == DEFAULT_PROCESS_RULE['rule']
  rule = SimpleNamespace(rule=DEFAULT_PROCESS_RULE['rule'])
  cleaned = ProcessRuleService.clean_text_by_process_rule(
    '你好  世界 https://example.com a@b.com', rule
  )
  assert cleaned.strip() == '你好 世界'
  splitter = ProcessRuleService.get_text_splitter_by_process_rule(rule)
  assert len(splitter.split_text('知识库。' * 600)) > 1
  with app.test_request_context(
    method='POST',
    json={
      'upload_file_ids': [str(uuid.uuid4())],
      'process_type': 'custom',
      'rule': {'pre_process_rules': [None]},
    },
  ):
    req = CreateDocumentsReq()
    assert not req.validate()


def test_celery_redis_auth_and_ssl(monkeypatch):
  monkeypatch.setenv('REDIS_USE_SSL', 'true')
  monkeypatch.setenv('REDIS_USERNAME', 'user@name')
  monkeypatch.setenv('REDIS_PASSWORD', 'pass:/word')
  config = Config()
  assert config.CELERY['broker_url'].startswith('rediss://user%40name:pass%3A%2Fword@')
  assert config.CELERY['broker_url'].endswith('?ssl_cert_reqs=required')
