from server.settings.util import config
import os
from django.urls import path
from server.settings import BASE_DIR
# debug 模式
DEBUG = config("DJANGO_DEBUG", True, cast=bool)

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "121.40.155.61",
    "47.99.93.160",
    "match.ziqiang.net.cn",
    "api.match.ziqiang.net.cn",
    "test.match.ziqiang.net.cn",
    "api.test.match.ziqiang.net.cn",
]

# 开发阶段这样写
MEDIA_ROOT = "static_files"
# 确保使用 OSS 存储（如果 storage.py 中已配置）
# 如果 OSS 配置失败，这里会使用默认的文件系统存储
SERVER_URL = config("SERVER_URL", "https://test.match.ziqiang.net.cn")

# 放开本地联调 CORS（生产环境仍使用白名单）
try:
    from server.settings.components.common import *  # noqa
    # 常见前端端口
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOW_CREDENTIALS = True
    CORS_ALLOW_HEADERS = (
        "authorization",
        "content-type",
        "x-requested-with",
    )
except Exception:
    pass
