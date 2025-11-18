from server.settings.util import config

# from server.settings.components.configs import CacheConfig

# debug 模式
DEBUG = config("DJANGO_DEBUG", False, cast=bool)

ALLOWED_HOSTS = [
    "match.ziqiang.net.cn",
    "api.match.ziqiang.net.cn",
]

SERVER_URL = config("SERVER_URL", "https://api.match.ziqiang.net.cn")
