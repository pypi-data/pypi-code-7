from __future__ import unicode_literals

import os as _os


__version__ = '0.4.3'


# TO use run:
# travis encrypt 'PYPI_PASSWORD=adsfasdfasdf' --add

config = dict(
    PYPI_USERNAME='omnibus',
    PYPI_PASSWORD=None,
    PYPI_INDEX='pypi.vandelay.io/balanced/prod/+simple/',
    PYPI_SERVER='https://pypi.vandelay.io/balanced/prod/',
    PUBLISH_BRANCH='master'
)


for k in config:
    config[k] = _os.environ.get(k, config[k])
