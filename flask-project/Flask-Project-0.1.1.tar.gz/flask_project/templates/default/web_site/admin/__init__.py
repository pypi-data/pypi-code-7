# coding=utf-8
from __future__ import unicode_literals, print_function
from flask.ext.admin import Admin
from flask.ext.admin.menu import MenuLink
from web_site.admin.views import IndexView
from flask.ext.admin.contrib.sqla import ModelView
from web_site import db
from web_site.user.models import Role, User


admin = Admin(index_view=IndexView(name=u'首页'))

admin.add_view(ModelView(Role, db.session, endpoint="model_role", category="User"))
admin.add_view(ModelView(User, db.session, endpoint="model_user", category="User"))


admin.add_link(MenuLink(u'返回前台', url='/'))
