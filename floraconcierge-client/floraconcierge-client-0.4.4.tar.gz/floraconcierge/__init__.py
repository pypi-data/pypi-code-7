VERSION = (0, 4, 4)


def get_version(*args, **kwargs):
    return ".".join(map(str, VERSION))

HTTP_CLIENT_UA = 'FloraConcierge Python Api Client v%s' % get_version()
