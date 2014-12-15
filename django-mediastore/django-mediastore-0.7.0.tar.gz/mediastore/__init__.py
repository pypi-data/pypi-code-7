import os
from django.conf import settings


def media_url(url):
    if hasattr(settings, 'STATIC_URL'):
        base_url = settings.STATIC_URL
    else:
        base_url = settings.MEDIA_URL
    return os.path.join(base_url, 'mediastore', url)
