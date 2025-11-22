import pymysql
pymysql.install_as_MySQLdb()



import sys
from os import environ
from pathlib import Path

from server.settings.util import *

from server.settings.components.apps import *
from server.settings.components.caches import *
from server.settings.components.common import *
from server.settings.components.databases import *
from server.settings.components.drf import *
from server.settings.components.email import *
from server.settings.components.simpleui import *
from server.settings.components.storage import *
from server.settings.components.zq_auth import *
from server.settings.components.wechat import *
from server.settings.components import *  # noqa

_ENV = environ.get("DJANGO_ENV", "development")

if _ENV == "development":
    from server.settings.environments.development import *  # noqa
elif _ENV == "production":
    from server.settings.environments.production import *  # noqa

# Build paths inside the project like this: BASE_DIR.joinpath('some')
# `pathlib` is better than writing: dirname(dirname(dirname(__file__)))
BASE_DIR = Path(__file__).parent.parent.parent
# 添加导包路径
sys.path.insert(0, str(BASE_DIR.joinpath("server", "apps")))
