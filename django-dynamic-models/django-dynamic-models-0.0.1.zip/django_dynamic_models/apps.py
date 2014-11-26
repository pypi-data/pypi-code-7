from django.apps import AppConfig
import django_dynamic_models

def _autodiscover(registry):
    """See documentation for autodiscover (without the underscore)"""
    import copy
    from django.conf import settings
    from django.utils.importlib import import_module
    from django.utils.module_loading import module_has_submodule

    for app in settings.INSTALLED_APPS:
        mod = import_module(app)
        # Attempt to import the app's.
        try:
            before_import_registry = copy.copy(registry)
            import_module('%s.models_changes_registry' % app)
        except:
            registry = before_import_registry

            # Decide whether to bubble up this error. If the app just
            # doesn't have an admin module, we can ignore the error
            # attempting to import it, otherwise we want it to bubble up.
            if module_has_submodule(mod, 'models_changes_registry'):
                raise

from changes import change
registry = change

from .apps import *

def autodiscover():
    """
    Check all apps in INSTALLED_APPS for stuff related to autocomplete.
    """
    
    _autodiscover(registry)

default_app_config = 'django_dynamic_models.apps.ProjectModelsConfig'

class ProjectModelsConfig(AppConfig):
    name = 'django_dynamic_models'
    autodiscover()