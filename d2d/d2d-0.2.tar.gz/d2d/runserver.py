import os
import sys
from django.core.management import execute_from_command_line

#----------------------------------------------------------------------
def runserver(settings):
    """"""
    sys.path.append(settings.APPNAME)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "%s.settings"%settings.APPNAME)
    execute_from_command_line([os.path.join(os.path.split(sys.argv[0])[0], settings.APPNAME, "manage.py"), "runserver", settings.PORT, "--noreload"])

