# coding: utf-8

"""
загрузка данных из приложения в систему
"""

import json
import os
import requests

from django.db.models import get_app
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management import call_command


URL = getattr(settings, SMOKNUR_URL, 'http://127.0.0.1:8000')
if not URL.startswith('http://'):
    URL = 'http://' + URL

class Command(BaseCommand):
    """загрузка данных из .dbg в систему"""

    args = 'app.core.app'
    help = 'send requests from .dbg'

    def handle(self, *args, **options):
        """-"""

        app = args[0]
        if app not in settings.INSTALLED_APPS:
            self.stdout.write(u"app ({0}) nor in settings.INSTALLED_APPS".format(app))
            return
        else:
            app = get_app(app)

        # авторизуем пользователя
        if (hasattr(settings, 'SMOKNUR_USERNAME') 
            and hasattr(settings, 'SMOKNUR_PASSWORD')):
            r = requests.post(
                url=URL + '/auth/login',
                data={'login_login': settings.SMOKNUR_USERNAME,
                      'login_password': settings.SMOKNUR_PASSWORD}
            )
            assert r.status_code == 200
        else:
            self.stdout.write(u"SMOKNUR_USERNAME, SMOKNUR_PASSWORD not in settings")
            return

        path = path = os.path.join(
            os.path.dirname(app.__file__),
            'smoknur')

        if os.path.exists(path):

            fixtures = [os.path.join(path, f) for f in sorted(os.listdir(path)) if f.endswith('.json')]
            
            if fixtures:
                call_command('loaddata', *fixtures,
                    **{'verbosity': 0, 
                    'database': db_name,
                    'skip_validation': True})                    

            for f in sorted(os.listdir(path)):
                if f.endswith('.dbg'):
                    with open(os.path.join(path, f)) as f_dbg:
                        for line in f_dbg:
                            if not line.startswith('#'):
                                req = json.loads(line)

                                r1 = requests.post(
                                    url=URL + req['url'],
                                    data=req['params'],
                                    cookies=r.cookies
                                )
                                assert r1.status_code == 200, u'{0}\n{1}'.format(url, r.text)
