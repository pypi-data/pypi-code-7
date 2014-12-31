from django.apps import AppConfig


class DefaultConfig(AppConfig):
    name = 'djangoquietrunserver'
    verbose_name = 'Quiet runserver-- command'


class MonkeypatchConfig(AppConfig):
    name = 'djangoquietrunserver'
    verbose_name = 'Quiet monkeypatched runserver command'

    def ready(self):
        from . import monkeypatch
        monkeypatch()
