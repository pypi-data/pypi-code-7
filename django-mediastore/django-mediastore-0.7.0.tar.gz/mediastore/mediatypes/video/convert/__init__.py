def get_convert_backend():
    from mediastore.mediatypes.video.conf import settings
    bits = settings.MEDIASTORE_VIDEO_BACKEND.split('.')
    module, obj = '.'.join(bits[:-1]), bits[-1]
    module = __import__(module, globals(), locals(), [obj], -1)
    backend = getattr(module, obj)
    return backend
