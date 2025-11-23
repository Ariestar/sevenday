from server.settings.util import config, BASE_DIR

# from server.settings.components.configs import CacheConfig

# debug 模式
DEBUG = config("DJANGO_DEBUG", False, cast=bool)

# ALLOWED_HOSTS 支持从环境变量读取，用逗号分隔
# 例如：DJANGO_ALLOWED_HOSTS=example.com,api.example.com,192.168.1.1
ALLOWED_HOSTS_ENV = config("DJANGO_ALLOWED_HOSTS", "")
if ALLOWED_HOSTS_ENV:
    # 从环境变量读取，支持逗号分隔
    ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_ENV.split(",") if host.strip()]
else:
    # 默认配置
    ALLOWED_HOSTS = [
        "match.ziqiang.net.cn",
        "api.match.ziqiang.net.cn",
        "47.99.93.160",
    ]

SERVER_URL = config("SERVER_URL", "https://api.match.ziqiang.net.cn")

# 生产环境媒体文件配置
MEDIA_ROOT = str(BASE_DIR.joinpath("static_files"))
