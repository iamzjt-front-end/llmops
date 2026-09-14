from langchain_community.tools.openai_dalle_image_generation import (
  OpenAIDALLEImageGenerationTool,
)
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


def dalle3(**kwargs) -> BaseTool:
  """返回dalle3绘图的LangChain工具"""
  return OpenAIDALLEImageGenerationTool(
    api_wrapper=DallEAPIWrapper(model='dall-e-3', **kwargs),
  )
