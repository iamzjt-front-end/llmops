import json
from pathlib import Path

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, message_to_dict, messages_from_dict


class FileChatMessageHistory(BaseChatMessageHistory):
  """基于文件持久化的对话历史存储，替代 langchain_community 的同名弃用实现"""

  def __init__(self, file_path: str):
    """初始化时确保存储目录存在"""
    self.file_path = Path(file_path)
    self.file_path.parent.mkdir(parents=True, exist_ok=True)

  @property
  def messages(self) -> list[BaseMessage]:
    """从文件中读取全部历史消息"""
    if not self.file_path.exists():
      return []
    items = json.loads(self.file_path.read_text(encoding='utf-8'))
    return messages_from_dict(items)

  def add_message(self, message: BaseMessage) -> None:
    """将一条消息追加到文件中"""
    items = [message_to_dict(m) for m in self.messages]
    items.append(message_to_dict(message))
    self.file_path.write_text(json.dumps(items, ensure_ascii=False), encoding='utf-8')

  def clear(self) -> None:
    """清空全部历史消息"""
    self.file_path.write_text('[]', encoding='utf-8')
