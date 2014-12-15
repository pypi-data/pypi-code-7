# coding=utf-8
from __future__ import unicode_literals, print_function
from flask import Blueprint

main_blueprint = Blueprint('main', __name__)

from web_site.main import views
