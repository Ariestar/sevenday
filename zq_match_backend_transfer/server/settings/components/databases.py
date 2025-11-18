import os

import dj_database_url
from loguru import logger

from server.settings.util import BASE_DIR, config

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DATABASE_URL = config(
    "DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "db.sqlite3")
)

if DATABASE_URL.startswith("mysql"):
    DATABASES = {
        "default": {
            **dj_database_url.parse(DATABASE_URL),
            "OPTIONS": {"charset": "utf8mb4"},
        }
    }

else:
    DATABASES = {"default": dj_database_url.parse(DATABASE_URL)}

logger.success(f"Database connect to: {DATABASES['default']['HOST']}")
