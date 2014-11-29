from hatak.plugin import Plugin
from .commands import TosterCommand


class TosterPlugin(Plugin):

    def __init__(self, fixtures):
        super().__init__()
        self.fixtures = fixtures

    def add_commands(self, parent):
        parent.add_command(TosterCommand(self.fixtures))
