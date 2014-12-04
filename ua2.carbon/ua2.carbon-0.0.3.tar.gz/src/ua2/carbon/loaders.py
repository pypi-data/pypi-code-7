
def django_loader():
    from .conf import settings
    from django.conf import settings as django_settings
    settings.set_parent(django_settings)
