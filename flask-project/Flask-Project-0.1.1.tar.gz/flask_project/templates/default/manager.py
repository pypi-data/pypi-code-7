#!/bin/env python
# coding=utf-8
from __future__ import unicode_literals, print_function
import os
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand
from web_site import create_app, db
from web_site.user.models import User, Role


app = create_app(os.getenv('SYSTEM_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


#####################################
# 数据库相关
#####################################
@manager.command
def prepare_db():
    db.create_all()
    Role.insert_roles()


@manager.command
def drop_db():
    db.drop_all()


@manager.option('-u', '--username', dest="username", required=True)
@manager.option('-e', '--email', dest="email", required=True)
@manager.option('-p', '--password', dest="password", required=True)
@manager.option('-r', '--role', dest="role_name", required=False)
def add_user(username, email, password, role_name="Administrator"):
    role = Role.query.filter_by(name=role_name).first()
    user = User(username=username, email=email, password=password, role=role)
    user.confirmed = True
    db.session.add(user)
    db.session.commit()


#####################################
# 测试相关
#####################################
@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    manager.run()
