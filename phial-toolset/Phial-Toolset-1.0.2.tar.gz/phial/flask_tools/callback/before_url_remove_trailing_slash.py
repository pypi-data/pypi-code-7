# -*- coding: utf-8 -*-
from flask import request, redirect


def     flask_before_url_remove_trailing_slash():
    if request.path != '/' and request.path.endswith('/'):
        return redirect(request.path[:-1])
