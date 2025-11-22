# Loading `.env` files
# See docs: https://gitlab.com/mkleehammer/autoconfig
from pathlib import Path

from decouple import AutoConfig

BASE_DIR = Path(__file__).parent.parent.parent
CONFIG_DIR = BASE_DIR / "config"


def _resolve_env_path():
    """
    优先在项目根目录寻找 .env；若不存在则回退到 config/ 目录
    """
    if (BASE_DIR / ".env").exists():
        return BASE_DIR
    if (CONFIG_DIR / ".env").exists():
        return CONFIG_DIR
    # 默认返回项目根目录，便于本地开发直接放置 .env
    return BASE_DIR


config = AutoConfig(search_path=_resolve_env_path())
