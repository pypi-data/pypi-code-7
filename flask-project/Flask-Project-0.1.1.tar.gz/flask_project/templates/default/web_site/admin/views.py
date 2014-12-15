# coding=utf-8
from __future__ import unicode_literals, print_function
from flask.ext.admin import expose, AdminIndexView
from flask.ext.login import current_user


class IndexView(AdminIndexView):
    @expose("/")
    def index(self):
        res = {
            'info': u'后台管理'
        }
        return self.render('admin/index.html', res=res)

    def is_accessible(self):
        return current_user.is_authenticated() and current_user.is_administrator()
