VERSION = (0, 4)


def get_version():
    return ".".join(map(str, VERSION))

__version__ = get_version()
