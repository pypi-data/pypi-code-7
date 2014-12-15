from django.core.management.base import BaseCommand
from mediastore.mediatypes.video.management import unlock, process_queue


class Command(BaseCommand):
    help = "Process all items stored in the video queue."

    def handle(self, *args, **options):
        if 'unlock' in args:
            unlock()
        process_queue()
