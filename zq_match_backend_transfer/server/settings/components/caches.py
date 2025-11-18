# Caching configuration
import urllib
import os

import django_cache_url
from loguru import logger

from server.settings.util import config

# If running in development, prefer a local in-memory cache to avoid requiring Redis
DJANGO_ENV = os.environ.get("DJANGO_ENV", "development")
if DJANGO_ENV == "development":
    CACHE_URL = os.environ.get("CACHE_URL", "locmem:///")
else:
    CACHE_URL = config("CACHE_URL", "locmem:///")

if CACHE_URL.endswith("/"):
    CACHE_URL = CACHE_URL[:-1]

CACHES = {
    "default": django_cache_url.parse(f"{CACHE_URL}/0"),
    "session": django_cache_url.parse(f"{CACHE_URL}/1"),
    "third_session": django_cache_url.parse(f"{CACHE_URL}/2"),
    "db_cache": django_cache_url.parse(f"{CACHE_URL}/3"),
    "view": django_cache_url.parse(f"{CACHE_URL}/4"),
    "celery": django_cache_url.parse(f"{CACHE_URL}/5"),
}

# Try to log cache hostname when available (may be None for locmem)
try:
    hostname = urllib.parse.urlparse(CACHES["default"]["LOCATION"]).hostname
except Exception:
    hostname = None
logger.success(f"Redis connect to: {hostname}")

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "session"

# region CACHEOPS
# https://github.com/Suor/django-cacheops

# if config("CACHE_URL", "").startswith("redis://"):
#     CACHEOPS_REDIS = config("CACHE_URL")
#     if CACHEOPS_REDIS.endswith("/"):
#         CACHEOPS_REDIS = CACHEOPS_REDIS[:-1]
#     CACHEOPS_REDIS = CACHEOPS_REDIS + "/9"  # 选择合适的redis编号
#
#     CACHEOPS_DEFAULTS = {"timeout": 5}
#
#     CACHEOPS = {
#         "users.*": {"ops": "all", "timeout": 60},
#     }

# endregion
