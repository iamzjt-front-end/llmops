from dataclasses import dataclass

from flask import Blueprint, Flask
from injector import inject

from internal.handler import AppHandler, BuiltinToolHandler


@inject
@dataclass
class Router:
  """路由"""

  app_handler: AppHandler
  builtin_tool_handler: BuiltinToolHandler

  def register(self, app: Flask):
    """注册路由"""

    # 1.创建一个蓝图
    bp = Blueprint('llmops', __name__, url_prefix='')

    # 2.将url与对应的控制器方法做绑定
    bp.add_url_rule(
      '/ping',
      methods=['GET'],
      view_func=self.app_handler.ping,
    )
    bp.add_url_rule(
      '/app/<uuid:app_id>/debug',
      methods=['POST'],
      view_func=self.app_handler.debug,
    )
    bp.add_url_rule(
      '/app',
      methods=['POST'],
      view_func=self.app_handler.create_app,
    )
    bp.add_url_rule(
      '/app/<uuid:app_id>',
      methods=['GET'],
      view_func=self.app_handler.get_app,
    )
    bp.add_url_rule(
      '/app/<uuid:app_id>',
      methods=['PUT'],
      view_func=self.app_handler.update_app,
    )
    bp.add_url_rule(
      '/app/<uuid:app_id>',
      methods=['DELETE'],
      view_func=self.app_handler.delete_app,
    )

    # 3.内置插件广场模块
    bp.add_url_rule(
      '/builtin-tools',
      methods=['GET'],
      view_func=self.builtin_tool_handler.get_builtin_tools,
    )
    bp.add_url_rule(
      '/builtin-tools/<string:provider_name>/tools/<string:tool_name>',
      methods=['GET'],
      view_func=self.builtin_tool_handler.get_provider_tool,
    )

    # 4.在应用上去注册蓝图
    app.register_blueprint(bp)
