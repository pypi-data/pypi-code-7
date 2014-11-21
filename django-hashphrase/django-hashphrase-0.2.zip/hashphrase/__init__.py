VERSION = (0, 2, 0)
__version__ = '.'.join(map(str, VERSION))
from helpers import Hashlink, hashphrase_register, init_package, hashphraseviews_autodiscover
init_package()