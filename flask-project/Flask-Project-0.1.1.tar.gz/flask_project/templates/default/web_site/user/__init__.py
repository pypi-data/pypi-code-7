# coding=utf-8
from __future__ import unicode_literals, print_function
from flask import Blueprint

user_blueprint = Blueprint('user', __name__)

from web_site.user import models, views
