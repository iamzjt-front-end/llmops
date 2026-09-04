import random

from langchain_core.runnables import RunnableLambda


def get_weather(location: str, unit: str, name: str) -> str:
  """根据传入的位置＋温度单位获取对应的天气信息"""
  print(f'location: {location}')
  print(f'unit: {unit}')
  print(f'name: {name}')
  return f'{location} 天气为 {random.randint(24, 40)} {unit}'


get_weather_runnable = RunnableLambda(get_weather).bind(unit='℃', name='zjt')
resp = get_weather_runnable.invoke('合肥')

print(resp)
