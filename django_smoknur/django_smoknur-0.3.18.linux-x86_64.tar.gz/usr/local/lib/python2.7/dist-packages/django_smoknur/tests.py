# coding: utf-8

"""
модуль базового теста
"""

import json
import os
import sys

import django
from django.conf import settings
from django.core.management import call_command
from django.db.models import get_apps
from django.http import HttpResponseRedirect
from django.test import TransactionTestCase

if (django.VERSION[:3] > (1, 5, 0) and
        getattr(settings, 'SMOKNUR_NEW_DJANGO_TESTCASE', True)):
    NEW_DJANGO_TESTCASE = True
else:
    NEW_DJANGO_TESTCASE = False


def _fixture_setup(self):
    """
    начиная с джанги 1.6, в данном методе отсутсвует вызов метода
    call_command('flush')
    поэтому выполняем данный загрузчик фикстур
    """
    for db_name in self._databases_names(include_mirrors=False):
        # Reset sequences
        if self.reset_sequences:
            self._reset_sequences(db_name)

        call_command('flush', verbosity=0, interactive=False, database=db_name)

        if hasattr(self, 'fixtures'):
            # We have to use this slightly awkward syntax due to the fact
            # that we're using *args and **kwargs together.

            call_command('loaddata', *self.fixtures,
                         **{'verbosity': 0, 'database': db_name,
                            'skip_validation': True})


def iter_tests(self):
    """
    проходим по всем файлам с тестами
    """
    for file_name in sorted(os.listdir(self.smoknur_path)):
        if file_name.endswith('.dbg'):
            yield file_name


def send_request(client, req):
    """
    прогоняем запрос

    если не указан метод запроса, то по умолчанию берется
    POST(для обратной совместимости)
    """

    method = req.get('method', "POST")

    if method == 'GET':
        resp = client.get(
            req['url'],
            req['params']
        )
    elif method == "POST":
        resp = client.post(
            req['url'],
            req['params']
        )
    #TODO добавить обработку других методов
    else:
        resp = None

    return resp


def run_test_line(self, req, index, file_name, output):
    """
    прогоняем одну строку теста
    """

    if getattr(settings, 'SMOKNUR_PRINT_REQUESTS', False):
        output.write(
            u'line={0}, file={1}, url={2}, '
            u'post_params={3}'.format(
                index,
                file_name,
                req['url'],
                req['params']).encode('utf-8'))

    try:
        resp = send_request(self.client, req)
    except:
        output.write(
            u'line={0}, file={1}, url={2}, '
            u'post_params={3}'.format(
                index,
                file_name,
                req['url'],
                req['params']).encode('utf-8'))
        raise
    else:
        if getattr(settings,
                   'SMOKNUR_PRINT_RESPONSE',
                   False):
            size = getattr(settings,
                           'SMOKNUR_PRINT_RESPONSE_SIZE',
                           0)
            output.write(
                u'{0}, {1}\n'.format(
                    resp.status_code,
                    resp.content[:size]).encode('utf-8'))

    message = (u'line={0}, file={1}, url={2}, post_params={3}, '
        u'status_code={4}').format(
            index,
            file_name,
            req['url'],
            req['params'],
            resp.status_code).encode('utf-8')
    if 'status_code' in req:
        self.assertTrue(
            resp.status_code == req['status_code'],
            message
        )
    else:
        self.assertTrue(
            resp.status_code in (200, 302),
            message
        )


def test_runner(self, output=sys.stdout):
    """
    smoke test
    """

    # отправляем пост запросы
    for file_name in iter_tests(self):
        with open(os.path.join(self.smoknur_path, file_name)) as f_dbg:
            for index, line in enumerate(f_dbg, 1):
                if not line.startswith('#'):
                    req = json.loads(line)
                    run_test_line(self, req, index, file_name, output)


exclude_apps = getattr(settings, 'SMOKNUR_EXCLUDE_APPS', ())

# добавляем в глобал тесткейсы
for app in get_apps():

    if app.__package__ in exclude_apps:
        continue

    path = os.path.join(
        os.path.dirname(app.__file__),
        'smoknur')

    if os.path.exists(path):

        smok_dirs = [
            os.path.join(path, f)
            for f in os.listdir(path)
            if os.path.isdir(os.path.join(path, f))]

        smok_dirs.append(path)

        for smok_dir in smok_dirs:

            # если в папке нет файлов запросов, игнорируем его
            if not [i for i in os.listdir(smok_dir) if i.endswith('.dbg')]:
                continue

            test_name = u'{0}_{1}'.format(
                app.__package__.replace('.', '_'),
                os.path.basename(smok_dir)
            ).upper().encode('utf-8')

            attrs = {
                'fixtures': [],
                'smoknur_path': smok_dir,
                'test': test_runner
            }

            if NEW_DJANGO_TESTCASE:
                attrs['_fixture_setup'] = _fixture_setup

            for file_ in sorted(os.listdir(smok_dir)):
                if file_.endswith('.json'):
                    attrs['fixtures'].append(os.path.join(smok_dir, file_))

            globals()[test_name] = type(
                test_name,
                (TransactionTestCase, ),
                attrs)

class DjangoSmoknurTest(TransactionTestCase):
    """
    тест самого django_smoknur
    """

    def test(self):

        self.check_debug_false()
        self.check_debug_true()

    def check_debug_false(self):
        """
        проверка экшенов при дебаг false
        """

        for url, context in (
                ('/smoknur', {}),
                ('/smoknur', {'action': 'dump_data'})
        ):
            response = self.client.get(url, context)
            self.check_redirect(response, '/')

    def check_debug_true(self):
        """
        проверка экшенов при дебаг екгу
        """

        settings.DEBUG = True

        # основное окно программы
        self.assertEqual(
            self.client.post('/smoknur').status_code,
            200
        )

        # скачиваем дамп
        response = self.client.get(
            '/smoknur',
            {
                'action': 'dump_data'
            })
        self.assertEqual(response.status_code, 302)

        self.assertTrue('location' in response._headers)
        self.assertTrue(
            response._headers['location'][1].endswith('.json'),
            response._headers['location'][1])

        # активация записи
        response = self.client.get(
            '/smoknur',
            {
                'action': 'activate'
            })

        self.assertEqual(response.status_code, 302)
        self.check_redirect(response, '/smoknur')

        self.assertIn('debug_on', response.cookies)
        self.assertTrue(response.cookies['debug_on'])

        # response.cookies[''] = Morsel объект
        self.assertIn('debug_file_path', response.cookies)
        debug_file_path = response.cookies['debug_file_path'].value
        self.assertTrue(debug_file_path.endswith('.dbg'))
        self.assertTrue(os.path.exists(debug_file_path))
        debug_file_size = os.stat(debug_file_path).st_size

        self.assertIn('debug_file_url', response.cookies)

        # некоторые переходы по урлам
        self.client.post('/', {})
        self.client.post('/auth/login', {})
        self.client.post('/auth/login', {'login': 'admin', 'password': 'admin'})
        self.client.post('/auth/logout', {})
        self.client.get('/', {})
        self.client.get('/auth/logout', {})
        self.client.get('/auth/logout', {'login': 'admin', 'password': 'admin'})

        # проверяем размер файлика
        self.assertTrue(os.stat(debug_file_path).st_size > debug_file_size)

        self.assertTrue(
            response.cookies['debug_file_url'].value.endswith('.dbg'))
        self.assertIn(
            settings.MEDIA_URL,
            response.cookies['debug_file_url'].value)

        # деактивация записи
        response = self.client.get(
            '/smoknur',
            {
                'action': 'deactivate'
            })

        self.assertEqual(response.status_code, 302)
        self.check_redirect(response, '/smoknur')

        self.assertIn('debug_on', response.cookies)
        self.assertTrue(response.cookies['debug_on'])

        # with open(debug_file_path) as f:
        #     for line in f.readlines():
        #         print line

        # качаем дебаг файл
        # медию он не отдаст, т.к. тесты запускаются при DEBUG = False
        # debug_file_url = response.cookies['debug_file_url'].value
        # if not debug_file_url.startswith('/'):
        #     debug_file_url = '/' + debug_file_url
        # response = self.client.post(
        #     debug_file_url
        # )


    def tearDown(self):

        settings.DEBUG = False

    def check_redirect(self, response, url):
        """
        проверяем редирект на домашнюю папку
        """

        self.assertEqual(302, response.status_code)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertTrue(
            response._headers['location'][1] == 'http://testserver' + url,
            response._headers['location'][1])