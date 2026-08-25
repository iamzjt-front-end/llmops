class TestAppHandler:
  """app控制器的测试类"""

  def test_completion(self, client):
    resp = client.post('/app/completion', json={'query': '你好，你是？'})
