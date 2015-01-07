from django.core.management.commands.test import Command as TestCommand

from jsdir.core import JSDir


class Command(TestCommand):

    def __init__(self):
        JSDir.set_use_finders(True)  # sets the value only for this thread
        super(Command, self).__init__()
