from pathlib import Path

from hoshino import Service, priv
from hoshino.log import new_logger
from hoshino.config import NICKNAME,MODULES_ON

log = new_logger('Git-Manage')
BOTNAME = NICKNAME if isinstance(NICKNAME, str) else list(NICKNAME)[0]

SV_HELP = 'nothing'
sv = Service('Git-Manage', manage_priv=priv.SUPERUSER, enable_on_default=False, help_=SV_HELP, visible=False)

MODULES_PATH = Path(__file__).parent.parent
ROOT = Path(__file__).parent
SAMPLE = ROOT / 'data' / 'sample.json'