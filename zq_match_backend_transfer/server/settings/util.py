# Loading `.env` files
# See docs: https://gitlab.com/mkleehammer/autoconfig
from pathlib import Path

from decouple import AutoConfig

BASE_DIR = Path(__file__).parent.parent.parent
config = AutoConfig(search_path=BASE_DIR.joinpath("config"))
