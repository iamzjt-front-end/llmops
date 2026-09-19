import queue
import time
import uuid
from queue import Queue
from threading import Event
from uuid import UUID

from redis import Redis

from internal.core.agent.entities.queue_entity import AgentQueueEvent, QueueEvent
from internal.entity.conversation_entity import InvokeFrom


class AgentQueueManager:
  """流式事件队列，支持心跳、停止、异常及超时。"""

  def __init__(
    self, user_id: UUID, task_id: UUID, invoke_from: InvokeFrom, redis_client: Redis
  ):
    self.q = Queue()
    self.user_id = user_id
    self.task_id = task_id
    self.invoke_from = invoke_from
    self.redis_client = redis_client
    self.closed = Event()
    prefix = (
      'account'
      if invoke_from in [InvokeFrom.WEB_APP, InvokeFrom.DEBUGGER]
      else 'end-user'
    )
    redis_client.setex(
      self.generate_task_belong_cache_key(task_id), 1800, f'{prefix}-{user_id}'
    )

  def listen(self, timeout: float = 600, ping_interval: float = 10):
    start = last_ping = time.monotonic()
    try:
      while True:
        try:
          item = self.q.get(timeout=min(1, max(timeout, 0.01)))
        except queue.Empty:
          item = None
          if self.closed.is_set():
            break
        else:
          if item is None:
            break
          yield item
          if item.event in {
            QueueEvent.STOP,
            QueueEvent.ERROR,
            QueueEvent.TIMEOUT,
            QueueEvent.AGENT_END,
          }:
            break
        now = time.monotonic()
        if now - start >= timeout:
          yield self._event(QueueEvent.TIMEOUT)
          break
        if self._is_stopped():
          yield self._event(QueueEvent.STOP)
          break
        if now - last_ping >= ping_interval:
          yield self._event(QueueEvent.PING)
          last_ping = now
    finally:
      self.closed.set()

  def _event(self, event, **kwargs):
    return AgentQueueEvent(id=uuid.uuid4(), task_id=self.task_id, event=event, **kwargs)

  def stop_listen(self):
    self.closed.set()
    self.q.put(None)

  def publish(self, agent_queue_event: AgentQueueEvent):
    if self.closed.is_set():
      return
    self.q.put(agent_queue_event)
    if agent_queue_event.event in {
      QueueEvent.STOP,
      QueueEvent.ERROR,
      QueueEvent.TIMEOUT,
      QueueEvent.AGENT_END,
    }:
      self.stop_listen()

  def publish_error(self, error):
    self.publish(self._event(QueueEvent.ERROR, observation=str(error)))

  def _is_stopped(self):
    return (
      self.redis_client.get(self.generate_task_stopped_cache_key(self.task_id))
      is not None
    )

  @classmethod
  def generate_task_belong_cache_key(cls, task_id: UUID):
    return f'generate_task_belong:{task_id}'

  @classmethod
  def generate_task_stopped_cache_key(cls, task_id: UUID):
    return f'generate_task_stopped:{task_id}'
