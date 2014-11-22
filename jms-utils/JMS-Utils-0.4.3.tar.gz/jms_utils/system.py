import platform
import sys


def get_system():
    if sys.platform == u'win32':
        platform_ = u'win'
    elif sys.platform == u'darwin':
        platform_ = u'mac'
    else:
        if u'x86_64' in platform.uname():
            platform_ = 'nix64'
        elif u'armv6l' in platform.uname():
            platform_ = u'arm'
        else:
            platform_ = u'nix'
    return platform_
