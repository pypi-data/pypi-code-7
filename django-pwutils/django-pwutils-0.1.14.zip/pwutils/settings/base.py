
import os

from django.utils import importlib

main_settings = importlib.import_module(os.environ.get('MAIN_SETTINGS', 'settings'))
local_vars = locals()
for k in dir(main_settings):
    local_vars[k] = getattr(main_settings, k)

try:
    PROJECT_ROOT
except NameError:
    # where manage.py lives
    PROJECT_ROOT = os.path.abspath(os.path.dirname(__name__))
