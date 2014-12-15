# coding=utf-8
from __future__ import unicode_literals, print_function
import os
from flask import Flask, render_template
from flask.ext.bootstrap import Bootstrap, ConditionalCDN, WebCDN
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.cache import Cache
from flask.ext.login import LoginManager
from flask.ext.mail import Mail
from flask.ext.moment import Moment
from flask_wtf.csrf import CsrfProtect
from flask.ext.uploads import configure_uploads
from raven.contrib.flask import Sentry
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.wsgi import SharedDataMiddleware
from config import CONFIGS


# plugins
db = SQLAlchemy()
mail = Mail()
cache = Cache()
bootstrap = Bootstrap()
moment = Moment()
login_manager = LoginManager()
sentry = Sentry()


def init_plugins(app):
    # db
    db.init_app(app)

    # admin
    from .admin import admin
    admin.init_app(app)

    # bootstrap && cdn
    bootstrap.init_app(app)
    init_cdn(app)

    # cache
    cache.init_app(app)

    # moment
    moment.init_app(app)

    # login
    login_manager.session_protection = 'strong'
    login_manager.login_view = 'user.login'
    login_manager.login_message_category = 'info'
    login_manager.needs_refresh_message = 'info'
    login_manager.init_app(app)

    # mail
    mail.init_app(app)


def init_cdn(app):
    static = app.extensions['bootstrap']['cdns']['static']
    local = app.extensions['bootstrap']['cdns']['local']

    def lwrap(cdn, primary=static):
        return ConditionalCDN('BOOTSTRAP_SERVE_LOCAL', primary, cdn)

    baidu = lwrap(WebCDN('//apps.bdimg.com/libs/'), local)
    app.extensions['bootstrap']['cdns']['baidu'] = baidu


def create_app(config_name):
    app = Flask(__name__)
    app.jinja_options['extensions'].append('jinja2.ext.loopcontrols')
    this_config = CONFIGS[config_name]
    this_config.init_app(app)
    app.config.from_object(this_config)

    CsrfProtect(app)
    if app.debug:
        DebugToolbarExtension(app)

        # serve static files during development
        app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {'/uploads': app.config.get('UPLOADS_DEFAULT_DEST')})
    else:
        sentry.init_app(app, dsn=app.config.get('SENTRY_DSN'))

    init_plugins(app)
    register_applications(app)
    register_error_handle(app)
    init_template(app)

    return app


def register_applications(app):
    from .main import main_blueprint
    from .user import user_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(user_blueprint, url_prefix='/user')


def register_error_handle(app):
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('error/403.html'), 403


    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error/404.html'), 404


    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('error/500.html'), 500


def init_template(app):
    from . import filters

    app.jinja_env.filters['identity'] = filters.identity

    @app.context_processor
    def register_context():
        return dict()

    app.jinja_env.globals['g_var'] = None
