from injector import Injector, inject


class A:
  name: str = 'llmops'


@inject
class B:
  def __init__(self, a: A):
    self.a = a

  def print(self):
    print(f'class A: {self.a.name}')


# 创建一个“自动组装对象”的管理员
injector = Injector()

# 告诉管理员：
# 我要一个 B，你自己看 B 需要什么，然后帮我组装好
b = injector.get(B)

b.print()
