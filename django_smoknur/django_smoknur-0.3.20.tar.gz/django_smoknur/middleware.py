# coding: utf-8

"""
модуль содержит мидлвары
"""

import json
import os


class WriteRequests(object):
    """
    мидлвара записывает запросы в файл

    параметры сессии для работы мидлвары

        debug_on - параметр, обозначает, включена ли отладочная запись
        debug_file_path - параметр, содержит путь к файлу для записи
        debug_file_url - содержит урл для скачивания

    """

    def process_response(self, request, response):
        """
        записываем параметры запроса и ответа
        """
        if (request.COOKIES.get('debug_on', False)
            and 'debug_file_path' in request.COOKIES
            and os.path.exists(request.COOKIES['debug_file_path'])
            and 'smoknur' not in request.META['PATH_INFO']
            and 'media' not in request.META['PATH_INFO']):
            # включена отладочная запись
            # имеется путь к файлу
            # файл существует
            # записываем отладочную информацию

            text = json.dumps({
                'url': request.META['PATH_INFO'],
                'params': request.POST,
                'status_code': response.status_code,
                'method': request.method
            })
            open(request.COOKIES['debug_file_path'], 'a').write(text + '\n')
        return response
