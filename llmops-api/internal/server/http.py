from flask import Flask

from config import Config
from internal.router import Router


class Http(Flask):
    """Http服务引擎"""

    def __init__(self, *args, conf: Config, router: Router, **kwargs):
        super().__init__(*args, **kwargs)
        self.config.from_object(conf)
        # 注册应用路由
        router.register(self)
