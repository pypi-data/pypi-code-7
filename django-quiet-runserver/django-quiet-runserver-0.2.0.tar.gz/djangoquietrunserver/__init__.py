__version_bits__ = (0, 2, 0)
__version__ = '.'.join(map(str, __version_bits__))


default_app_config = 'djangoquietrunserver.apps.DefaultConfig'


def monkeypatch():
    from djangoquietrunserver.requesthandler import run
    from django.core.servers import basehttp
    basehttp.run = run
