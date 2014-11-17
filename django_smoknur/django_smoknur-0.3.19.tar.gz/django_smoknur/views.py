# coding: utf-8

"""
модуль представлений приложения
"""

from cStringIO import StringIO
import os
import time

from django.core import management
from django.conf import settings
from django.shortcuts import render_to_response, redirect


def debug(request):
    """
    обработчик страницы информации приложения

    также обрабатывает гет запросы включения, выключения
        записи отладочной информации
    удаления файла отладки
    """
    if not settings.DEBUG:
        return redirect('/')

    action = request.GET.get('action', None)
    # import ipdb;ipdb.set_trace()
    response = redirect('/smoknur')
    if action == 'activate':
        # активация отладчика
        prefix = str(time.time()) + '.dbg'
        response.set_cookie('debug_on', True)
        response.set_cookie('debug_file_path', os.path.join(settings.MEDIA_ROOT,
                                                          prefix))
        response.set_cookie('debug_file_url', os.path.join(settings.MEDIA_URL,
                                                         prefix))
        open(response.cookies.get('debug_file_path').value, 'w')


    elif action == 'deactivate':
        # выключение отладчика
        response.delete_cookie('debug_on')

    elif (action == 'delete'
          and 'debug_file_path' in request.COOKIES
          and os.path.exists(request.COOKIES['debug_file_path'])):
        # удаление файла дампа
        os.remove(request.COOKIES['debug_file_path'])
        response.set_cookie('debug_on', False)
        response.delete_cookie('debug_file_path')
        response.delete_cookie('debug_file_url')
    elif action == 'dump_data':
        # выгрузка дампа БД
        buf = StringIO()
        management.call_command(
            'dumpdata',
            stdout=buf,
            indent=4,
            exclude=getattr(settings, 'SMOKNUR_EXCLUDE_APP_DUMPDATA', ()))
        prefix = str(time.time()) + '.json'
        buf.seek(0)
        open(os.path.join(settings.MEDIA_ROOT, prefix), 'w').write(buf.read())
        response = redirect('/media/' + prefix)
    else:
        response = render_to_response(
            'debug.html',
            {
                'debug_on': request.COOKIES.get('debug_on', None),
                'debug_file_path': request.COOKIES.get('debug_file_path', None),
                'debug_file_url': request.COOKIES.get('debug_file_url', None)
            })
    return response
