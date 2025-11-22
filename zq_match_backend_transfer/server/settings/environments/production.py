from server.settings.util import config, BASE_DIR

# from server.settings.components.configs import CacheConfig

# debug 模式
DEBUG = config("DJANGO_DEBUG", False, cast=bool)

ALLOWED_HOSTS = [
    "match.ziqiang.net.cn",
    "api.match.ziqiang.net.cn",
    "121.40.155.61",
]

SERVER_URL = config("SERVER_URL", "https://api.match.ziqiang.net.cn")

# 生产环境媒体文件配置
MEDIA_ROOT = str(BASE_DIR.joinpath("static_files"))
