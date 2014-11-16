# -*- coding: utf-8 -*-
from flask import Flask, render_template
from werkzeug.contrib.fixers import ProxyFix
from logging import Formatter, ERROR
from logging.handlers import RotatingFileHandler, SMTPHandler
from .flask_tools import FlaskURLMapRegexConverter
from .jinja_tools import jinja_get_translation_engine
import argparse
import sys


class   Phial(object):
    def __init__(self, appname, settings='settings'):
        self.__appname = appname
        self.__settings = __import__('%s.%s' % (appname, settings), fromlist=[settings.split('.')[1:]])
        self.__flask = None
        self.__celery = None

    def __default_debug_404(self, error):
        from flask import request
        from . import __version__ as phial_version
        return render_template('phial/default_debug_404.html', phial_version = phial_version, error = error, method=request.method, path=request.path, lst_route = self.__flask.url_map.iter_rules()), 404

    def __default_welcome(self):
        from . import __version__ as phial_version
        return render_template('phial/default_welcome.html', phial_version = phial_version)

    def initApp(self, **kwargs):
        # Initialize Flask
        self.__flask = Flask(import_name     = self.__appname,
                             template_folder = self.__settings.FLASK_TEMPLATES_DIR,
                             static_folder   = self.__settings.FLASK_STATIC_DIR,
                             **kwargs)
        self.__flask.secret_key = self.__settings.SECRET_KEY

        # Init G
        from . import g
        setattr(g, '__cur_phial', self)
        setattr(g, '__settings', self.__settings)

        # WSGI support
        self.__flask.wsgi_app = ProxyFix(self.__flask.wsgi_app)

        # Fix UTF-8 issue on python 2.x
        if sys.version_info[0] < 3:
            reload(sys)
            sys.setdefaultencoding('utf-8')

        # Add regex on Flask URL map
        self.__flask.url_map.converters['regex'] = FlaskURLMapRegexConverter

        # Init Peewee
        from .peewee_tools import base_model as peewee_bm
        if peewee_bm.BaseModel is not None and getattr(self.__settings, 'DATABASE_CONN_STRING', None) is not None:
            if self.__settings.DATABASE_CONN_STRING.startswith('mysql://') is True:
                # Load lib
                try:
                    from peewee import MySQLDatabase
                except ImportError:
                    print('[Phial][ERRO] MySQL driver is not installed (pip install MySQL-python or PyMySQL)')
                    sys.exit(1)
                peewee_bm.gl_database_type = 1
                hdl = MySQLDatabase(None)

                # Override Peewee init to work with connstring
                from .peewee_tools import peewee_overrided_database_init
                from peewee import Database
                funcType = type(Database.init)
                hdl.init = funcType(peewee_overrided_database_init, hdl, Database)

                # Register to Proxy
                peewee_bm.gl_database.initialize(hdl)
            elif self.__settings.DATABASE_CONN_STRING.startswith('sqlite') is True:
                # Load lib
                try:
                    from peewee import SqliteDatabase
                except ImportError:
                    print('[Phial][ERRO] sqlite3 is not installed')
                    sys.exit(1)
                peewee_bm.gl_database_type = 2
                hdl = SqliteDatabase(None)

                # Override Peewee init to work with connstring
                from .peewee_tools import peewee_overrided_database_init
                from peewee import Database
                funcType = type(Database.init)
                hdl.init = funcType(peewee_overrided_database_init, hdl, Database)

                # Register to Proxy
                peewee_bm.gl_database.initialize(hdl)
            else:
                print('[Phial][ERRO] Database backend not supported')
                sys.exit(1)

            # Init Database
            peewee_bm.gl_database.init(self.__settings.DATABASE_CONN_STRING)

        # Session handler
        if (getattr(self.__settings, 'FLASK_SESSION_HANDLER', None) and getattr(self.__settings, 'FLASK_SESSION_HANDLER_CFG', None)) is not None:
            try:
                mod_path = self.__settings.FLASK_SESSION_HANDLER.rsplit('.', 1)[0]
                class_name = self.__settings.FLASK_SESSION_HANDLER.split('.')[-1]
                hdl = __import__(mod_path, fromlist=[mod_path.split('.')[-1]])
                sess_handler = getattr(hdl, class_name)
                try:
                    self.__flask.session_interface = sess_handler(**self.__settings.FLASK_SESSION_HANDLER_CFG)
                except:
                    print('[Phial][ERRO] Session handler is misconfigured')
                    sys.exit(1)
            except (ImportError, AttributeError) as e:
                print("[Phial][ERRO] Can't load session backend \"%s\": %s" % (self.__settings.FLASK_SESSION_HANDLER, e))
                sys.exit(1)

        # Load user-defined routes
        try:
            url_map = __import__('%s.routes' % self.__appname, fromlist=['routes'])
            for u in getattr(url_map, 'routes', []):
                try:
                    try:
                        self.__flask.add_url_rule(u[0], view_func=u[1], methods=u[2], defaults=u[3])
                    except IndexError:
                        self.__flask.add_url_rule(u[0], view_func=u[1], methods=u[2])
                except AttributeError:
                    print('[Phial][WARN] Ignoring bad route entry: %s' % str(u))
            for u in getattr(url_map, 'errors', []):
                self.__flask.error_handler_spec[None][u[0]] = u[1]
        except ImportError:
            try:
                from cStringIO import StringIO
            except ImportError:
                from StringIO import StringIO
            import traceback
            stream_output = StringIO()
            traceback.print_exc(file=stream_output)
            print('[Phial][ERRO] File "%s.routes" does not exist or contain some errors...' % (self.__appname))
            print(stream_output.getvalue())
            sys.exit(1)

        # Set default welcome page if user-defined routes map is empty
        if len(self.__flask.url_map._rules) < 2:
            from os.path import dirname, join
            self.__flask.template_folder = join(dirname(__file__), 'assets/templates')
            self.__flask.static_folder = join(dirname(__file__), 'assets/static')
            self.__flask.add_url_rule('/', view_func=self.__default_welcome, methods=['GET'])

        # If application DEBUG==True -> redefine 404 error page
        if self.__settings.FLASK_DEBUG is True:
            self.__flask.error_handler_spec[None][404] = self.__default_debug_404

        # Jinja2 DEBUG
        self.__flask.jinja_env.globals.update({'DEBUG' : self.__settings.FLASK_DEBUG})

        # Jinja2 built-in extensions
        self.__flask.jinja_env.add_extension('jinja2.ext.do')
        self.__flask.jinja_env.add_extension('jinja2.ext.with_')
        self.__flask.jinja_env.add_extension('jinja2.ext.i18n')
        self.__flask.jinja_env.add_extension('phial.jinja_tools.ext.SelectiveHTMLCompress')
        self.__flask.jinja_env.add_extension('phial.jinja_tools.ext.DatetimeExtension')

        # Jinja2 i18n callables
        self.__flask.jinja_env.install_gettext_callables(
            lambda x: jinja_get_translation_engine().ugettext(x),
            lambda s, p, n: jinja_get_translation_engine().ungettext(s, p, n),
            newstyle = True)

        # Jinja2 user-defined extensions
        mod_path = getattr(self.__settings, 'JINJA_CUSTOM_EXTENSION_DIR', '%s.phial.jinja.extension' % self.__appname)
        try:
            hdl = __import__(mod_path, fromlist=[mod_path.split('.')[-1]])
            for im in getattr(hdl, '__all__', []):
                try:
                    self.__flask.jinja_env.add_extension('%s.%s' % (mod_path, im))
                except AttributeError:
                    print('[Phial][WARN] Extension "%s.%s" does not exist' % (mod_path, im))
        except ImportError:
            pass

        # Jinja2 user-defined filters
        mod_path = getattr(self.__settings, 'JINJA_CUSTOM_FILTER_DIR', '%s.phial.jinja.filter' % self.__appname)
        try:
            hdl = __import__(mod_path, fromlist=[mod_path.split('.')[-1]])
            for im in getattr(hdl, '__all__', []):
                item_hdl = getattr(hdl, im, None)
                if item_hdl is not None:
                    self.__flask.jinja_env.filters.update({im : item_hdl})
                else:
                    print('[Phial][WARN] Filter "%s.%s" does not exist' % (mod_path, im))
        except ImportError:
            pass

        # Jinja2 user-defined functions
        mod_path = getattr(self.__settings, 'JINJA_CUSTOM_FUNCTION_DIR', '%s.phial.jinja.function' % self.__appname)
        try:
            hdl = __import__(mod_path, fromlist=[mod_path.split('.')[-1]])
            for im in getattr(hdl, '__all__', []):
                item_hdl = getattr(hdl, im, None)
                if item_hdl is not None:
                    self.__flask.jinja_env.globals.update({im : item_hdl})
                else:
                    print('[Phial][WARN] Function "%s.%s" does not exist' % (mod_path, im))
        except ImportError:
            pass

        # Register before & after callback
        from .flask_tools.callback import flask_before_url_remove_trailing_slash, flask_before_i18n_set_user_language
        from .flask_tools.callback import flask_before_peewee_connect, flask_after_peewee_close
        self.__flask.before_request(flask_before_url_remove_trailing_slash)
        self.__flask.before_request(flask_before_peewee_connect)
        self.__flask.before_request(flask_before_i18n_set_user_language)
        self.__flask.after_request(flask_after_peewee_close)
        for im in getattr(self.__settings, 'FLASK_REQUEST_CALLBACK', []):
            try:
                mod_path = im[1].rsplit('.', 1)[0]
                class_name = im[1].split('.')[-1]
                hdl = __import__(mod_path, fromlist=[mod_path.split('.')[-1]])
                call_hdl = getattr(hdl, class_name)
                if im[0] == 'before':
                    self.__flask.before_request(call_hdl)
                elif im[0] == 'after':
                    self.__flask.after_request(call_hdl)
            except (ImportError, AttributeError) as e:
                print("[Phial][WARN] Can't load flask callback \"%s\": %s" % (im[1], e))
            except IndexError:
                print('[Phial][ERRO] FLASK_REQUEST_CALLBACK is misconfigured: %s' % e)
                sys.exit(1)

        # Register Celery (if lib is installed) and settings OK
        if getattr(self.__settings, 'CELERY_BROKER_URL', None) is not None:
            try:
                from celery import Celery
            except ImportError:
                print('[Phial][ERRO] Celery is not installed (pip install -U celery)')
                sys.exit(1)
            else:
                self.__flask.config.update(CELERY_BROKER_URL     = self.__settings.CELERY_BROKER_URL,
                                           CELERY_RESULT_BACKEND = getattr(self.__settings, 'CELERY_RESULT_BACKEND'),
                                           CELERY_ACCEPT_CONTENT = getattr(self.__settings, 'CELERY_ACCEPT_CONTENT'))
                self.__celery = Celery(main    = self.__flask.import_name,
                                       broker  = self.__flask.config['CELERY_BROKER_URL'],
                                       backend = self.__flask.config['CELERY_RESULT_BACKEND'])
                self.__celery.config_from_object(self.__flask.config)

                # Override Task to set the Flask app context
                TaskBase = self.__celery.Task

                class   ContextTask(TaskBase):
                    abstract = True

                    def __call__(self, *args, **kwargs):
                        from . import current_phial
                        with current_phial.flaskapp.app_context():
                            return TaskBase.__call__(self, *args, **kwargs)
                setattr(self.__celery, 'Task', ContextTask)

                # Register to globals
                setattr(g, '__celery', self.__celery)

                # Register tasks
                mod_path = getattr(self.__settings, 'CELERY_CUSTOM_TASKS_DIR', '%s.celery' % self.__appname)
                try:
                    hdl = __import__(mod_path, fromlist=[mod_path.split('.')[-1]])
                    for im in getattr(hdl, '__all__', []):
                        item_hdl = getattr(hdl, im, None)
                        if item_hdl is not None:
                            self.__celery.tasks.register(item_hdl)
                        else:
                            print('[Phial][WARN] Async task "%s.%s" does not exist' % (mod_path, im))
                except ImportError as e:
                    print("[Phial][ERRO] Can't load celery async tasks: %s" % e)
                    sys.exit(1)

        # Register error handlers (RELEASE MODE ONLY)
        if self.__settings.FLASK_DEBUG is False and len(self.__settings.ADMINS) > 0 and len(self.__settings.MAIL_USERNAME) > 0:
            hMailHandler = SMTPHandler((self.__settings.MAIL_SMTP, self.__settings.MAIL_SMTP_PORT),
                                       self.__settings.MAIL_USERNAME,
                                       [a[1] for a in self.__settings.ADMINS],
                                       self.__settings.LOGGING_MAIL_TITLE,
                                       (self.__settings.MAIL_USERNAME, self.__settings.MAIL_PASSWORD))
            if getattr(self.__settings, 'LOGGING_MAIL_TEMPLATE', None) is not None:
                hMailHandler.setFormatter(Formatter(self.__settings.LOGGING_MAIL_TEMPLATE))
            hMailHandler.setLevel(ERROR)
            self.__flask.logger.addHandler(hMailHandler)
        hFileHandler = RotatingFileHandler(self.__settings.LOGGING_FILE_FILENAME, 'a', self.__settings.LOGGING_FILE_MAXSIZE, self.__settings.LOGGING_FILE_NBROTATE)
        if getattr(self.__settings, 'LOGGING_FILE_TEMPLATE', None) is not None:
            hFileHandler.setFormatter(Formatter(self.__settings.LOGGING_FILE_TEMPLATE))
        hFileHandler.setLevel(ERROR)
        self.__flask.logger.addHandler(hFileHandler)

    @property
    def appname(self):
        return self.__appname

    @property
    def flaskapp(self):
        return self.__flask

    @property
    def celery(self):
        return self.__celery

    @property
    def settings(self):
        return self.__settings

    def startApp(self):
        # Create arguments parser
        parser = argparse.ArgumentParser(prog='phial')

        # Add built-in modules and retrieve user-defined modules
        lst_management = [
            ('help', parser.print_help, False)
            ]
        mod_path = 'phial.phial_management'
        try:
            hdl = __import__(mod_path, fromlist=[mod_path.split('.')[-1]])
            for im in getattr(hdl, '__all__', []):
                item_hdl = getattr(hdl, im, None)
                if item_hdl is not None:
                    lst_management.append((item_hdl.initParser(parser), item_hdl, True))
                else:
                    print('[Phial][WARN] Management class "%s.%s" does not exist' % (mod_path, im))
        except ImportError:
            pass
        mod_path = getattr(self.__settings, 'PHIAL_CUSTOM_MANAGEMENT_DIR', '%s.phial.management' % self.__appname)
        try:
            hdl = __import__(mod_path, fromlist=[mod_path.split('.')[-1]])
            for im in getattr(hdl, '__all__', []):
                item_hdl = getattr(hdl, im, None)
                if item_hdl is not None:
                    lst_management.append((item_hdl.initParser(parser), item_hdl, True))
                else:
                    print('[Phial][WARN] Management class "%s.%s" does not exist' % (mod_path, im))
        except ImportError:
            pass

        # Check arguements and run command
        from .flask_tools.callback import flask_before_i18n_set_user_language
        res = vars(parser.parse_args())
        for m in lst_management:
            if res.get(m[0], None) is not None:
                if m[0] != 'server':
                    with self.__flask.test_request_context():
                        flask_before_i18n_set_user_language('en')
                        if m[1]() if m[2] is False else m[1]().run(self, res) is True:
                            break
                else:
                    if m[1]() if m[2] is False else m[1]().run(self, res) is True:
                        break

    def runServer(self):
        self.__flask.run(host         = self.__settings.FLASK_LISTEN_ADDRESS,
                         port         = self.__settings.FLASK_LISTEN_PORT,
                         debug        = self.__settings.FLASK_DEBUG,
                         use_reloader = self.__settings.FLASK_USE_RELOADER,
                         threaded     = getattr(self.__settings, 'FLASK_THREADED_DEBUG_SERVER', False))
