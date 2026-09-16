from wtforms import Field


class ListField(Field):
  """自定义list字段，用于存储列表型数据"""

  data: list = None

  def process_formdata(self, values):
    if values is not None and isinstance(values, list):
      self.data = values

  def _value(self):
    return self.data if self.data else []
