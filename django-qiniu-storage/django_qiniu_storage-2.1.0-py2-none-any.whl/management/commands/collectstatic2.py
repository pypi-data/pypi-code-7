# -*- coding: utf-8 -*-

from optparse import make_option

from django.conf import settings
from django.core.management.base import CommandError
from django.contrib.staticfiles.management.commands import collectstatic
from django.contrib.staticfiles.storage import staticfiles_storage


from qiniustorage.backends import QiniuStorage

try:
    from django.utils.six.moves import input as _input
except ImportError:
    _input = raw_input


class Command(collectstatic.Command):
    """
    Override Django's build-in collectstatic command, and
    speed up the file uploading process.
    """

    help = "Collect static files in a single location, and upload \
those statics to the Qiniu Cloud Storage."

    option_list = collectstatic.Command.option_list + (
        make_option(
            '--no-upload',
            action="store_true",
            dest="no_upload",
            default=False,
            help="You need to manually..."
        ),
    )

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.local_storage = staticfiles_storage
        self.remote_storage = QiniuStorage()
        # del self.storage

    def set_options(self, **options):
        super(Command, self).set_options(**options)
        self.no_upload = options['no_upload']
        if self.symlink and not self.no_upload:
            raise CommandError("--symlink only works when --no-upload is enabled.")

    def handle_noargs(self, **options):
        self.set_options(**options)
        # Warn before doing anything more.

        destination_path = settings.STATIC_ROOT
        if self.no_upload:
            destination_display = ':\n\n    %s' % destination_path
        else:
            destination_display = '.'

        if self.clear:
            clear_display = 'This will DELETE EXISTING FILES!'
        else:
            clear_display = 'This will overwrite existing files!'

        if self.interactive:
            confirm = _input("""
You have requested to collect static files at the destination
location as specified in your settings%s
%s
Are you sure you want to do this?
Type 'yes' to continue, or 'no' to cancel: """
% (destination_display, clear_display))
            if confirm != 'yes':
                raise CommandError("Collecting static files cancelled.")

        collected = self.collect()
        modified_count = len(collected['modified'])
        unmodified_count = len(collected['unmodified'])
        post_processed_count = len(collected['post_processed'])

        if self.verbosity >= 1:
            template = ("\n%(modified_count)s %(identifier)s %(action)s"
                        "%(destination)s%(unmodified)s%(post_processed)s.\n")
            summary = template % {
                'modified_count': modified_count,
                'identifier': 'static file' + ('' if modified_count == 1 else 's'),
                'action': 'symlinked' if self.symlink else 'copied',
                'destination': (" to '%s'" % destination_path if destination_path else ''),
                'unmodified': (', %s unmodified' % unmodified_count if collected['unmodified'] else ''),
                'post_processed': (collected['post_processed'] and
                                   ', %s post-processed'
                                   % post_processed_count or ''),
            }
            self.stdout.write(summary)

    def copy_file(self, path, prefixed_path, source_storage):
        super(Command, self).copy_file(path, prefixed_path, self.local_storage)

    def delete_file(self, path, prefixed_path, source_storage):
        super(Command, self).delete_file(path, prefixed_path, self.local_storage)