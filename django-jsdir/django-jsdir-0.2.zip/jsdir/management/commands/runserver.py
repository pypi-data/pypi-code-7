from django.contrib.staticfiles.management.commands.runserver \
    import Command as StaticFilesCommand

from jsdir.core import JSDir


class Command(StaticFilesCommand):

    def __init__(self):
        JSDir.set_use_finders(True)  # sets the value only for this thread
        super(Command, self).__init__()
