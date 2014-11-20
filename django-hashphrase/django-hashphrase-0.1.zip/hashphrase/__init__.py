VERSION = (0, 1, 0)
__version__ = '.'.join(map(str, VERSION))
from helpers import Hashlink, hashphrase_register, init_package
init_package()