VERSION = (0, 3, 0)
__version__ = '.'.join(map(str, VERSION))
from helpers import hashphrase_register, init_package, hashphraseviews_autodiscover
from models import generate_hashphrase, HashLink
init_package()