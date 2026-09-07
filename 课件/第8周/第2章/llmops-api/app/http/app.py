#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/3/29 15:18
@Author  : thezehui@gmail.com
@File    : app.py
"""
import dotenv
from flask_migrate import Migrate

from config import Config
from internal.router import Router
from internal.server import Http
from pkg.sqlalchemy import SQLAlchemy
from .module import injector

# 1.将env加载到环境变量中
dotenv.load_dotenv()

# 2.构建LLMOps项目配置
conf = Config()

app = Http(
    __name__,
    conf=conf,
    db=injector.get(SQLAlchemy),
    migrate=injector.get(Migrate),
    router=injector.get(Router),
)

celery = app.extensions["celery"]

if __name__ == "__main__":
    app.run(debug=True)
