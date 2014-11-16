import time


def _get_version(v):
    version = '{}.{}'.format(v[0], v[1])
    if v[2]:
        version = '{}.{}'.format(version, v[2])
    if len(v) >= 4 and v[3]:
        version = '{}-{}'.format(version, v[3])
        if v[3] == 'dev' and len(v) >= 5 and v[4] > 0:
            version = '{}{}'.format(version, v[4])
    return version


def get_build():
    total = 0
    for i in list(time.localtime(time.time())):
        total += int(i)
    return total
