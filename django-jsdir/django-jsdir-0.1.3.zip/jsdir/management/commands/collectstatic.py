import os

from django.contrib.staticfiles.management.commands.collectstatic \
    import Command as StaticFilesCommand
from django.conf import settings

from jsdir.core import JSDir, jsdir_ext


class Command(StaticFilesCommand):

    def handle_noargs(self, **options):
        self.jsdirs = []
        super(Command, self).handle_noargs(**options)

        js_dir = os.path.join(settings.STATIC_ROOT,
                              getattr(settings, 'JSDIR_JSURL', 'js'))

        for dirpath, __, files in os.walk(js_dir):
            for f in files:
                if f.endswith(jsdir_ext):
                    dir_path = os.path.join(dirpath, f[:-len(jsdir_ext)]) \
                                   .replace(js_dir, '') \
                                   .replace('\\', '/').strip('/')
                    JSDir(dir_path).concatenate()

        # the directories for which no .dir.js file is generated will be
        # processed during the first request through the {% jsdir %} tag
