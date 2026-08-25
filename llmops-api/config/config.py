class Config:
  def __init__(self):
    # 关闭 WTF 的 CSRF 保护
    self.WTF_CSRF_ENABLED = False
