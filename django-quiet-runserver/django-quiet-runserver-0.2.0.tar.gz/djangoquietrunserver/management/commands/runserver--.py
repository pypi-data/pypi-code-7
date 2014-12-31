from djangoquietrunserver import monkeypatch

monkeypatch()

from django.core.management.commands.runserver import Command
