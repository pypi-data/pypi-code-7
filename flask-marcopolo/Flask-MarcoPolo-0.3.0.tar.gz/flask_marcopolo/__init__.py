"""
Flask-MarcoPolo

Flask-MarcoPolo is a Flask extension that adds structure to both your views and
templates, by mapping them to each other to provide a rapid application development framework.
The extension also comes with Flask-Classy, Flask-Assets, Flask-Mail,
JQuery 2.x, Bootstrap 3.x, Font-Awesome, Bootswatch templates.
The extension also provides pre-made templates for error pages and macros.

https://github.com/mardix/flask-marcopolo

"""

from flask import render_template, request, flash, get_flashed_messages
from werkzeug.contrib.fixers import ProxyFix
from flask.ext.classy import FlaskView, route  # flask-classy
from flask.ext.assets import Environment  # flask-assets
import inspect

__NAME__ = "Flask-MarcoPolo"
__version__ = "0.3.0"
__author__ = "Mardix"
__license__ = "MIT"
__copyright__ = "(c) 2014 Mardix"

#-------------------------------------------------------------------------------

# Flash Messages: error, success, info
def flash_error(message):
    """
    Set an `error` flash message
    :param message: string - The message
    """
    flash(message, "error")


def flash_success(message):
    """
    Set a `success` flash message
    :param message: string - The message
    """
    flash(message, "success")


def flash_info(message):
    """
    Set an `info` flash message
    :param message: string - The message
    """
    flash(message, "info")


# COOKIES: set, get, delete
def set_cookie(key, value="", **kwargs):
    """
    Set a cookie

    :param key: the key (name) of the cookie to be set.
    :param value: the value of the cookie.
    :param max_age: should be a number of seconds, or `None` (default) if
                    the cookie should last only as long as the client's
                    browser session.
    :param expires: should be a `datetime` object or UNIX timestamp.
    :param domain: if you want to set a cross-domain cookie.  For example,
                   ``domain=".example.com"`` will set a cookie that is
                   readable by the domain ``www.example.com``,
                   ``foo.example.com`` etc.  Otherwise, a cookie will only
                   be readable by the domain that set it.
    :param path: limits the cookie to a given path, per default it will
                 span the whole domain.
    """
    kwargs.update({"key": key, "value": value})
    MarcoPolo._set_cookie_ = kwargs


def get_cookie(key):
    """
    Get cookie
    """
    return request.cookies.get(key)


def del_cookie(key, path='/', domain=None):
    """
    Delete a cookie.  Fails silently if key doesn't exist.

    :param key: the key (name) of the cookie to be deleted.
    :param path: if the cookie that should be deleted was limited to a
                 path, the path has to be defined here.
    :param domain: if the cookie that should be deleted was limited to a
                   domain, that domain has to be defined here.
    """
    set_cookie(key=key, value='', expires=0, max_age=0, path=path, domain=domain)

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------


class MarcoPolo(FlaskView):
    """
    MarcoPolo a FlaskView extension
    """
    LAYOUT = "layout.html"  # The default layout
    assets = None
    _app = None
    _init_app_ = set()
    _set_cookie_ = None

    _UTILITY_PAGE_INFO = dict()

    @classmethod
    def init_app(cls, app):
        """
        To register application that needs the 'app' object to init
        :param app: callable function that will receive 'Flask.app' as first arg
        """
        if not hasattr(app, "__call__"):
            raise TypeError("From MarcoPolo.init_app: '%s' is not callable" % app)
        cls._init_app_.add(app)

    @classmethod
    def init(cls,
             app,
             config=None,
             project_dir="./app",
             proxyfix=True):
        """
        Allow to register all subclasses of MarcoPolo
        So we call it once initiating
        :param app: The app
        :param config: string of config object. ie: "app.config.Dev"
        :param project_dir: The directory containing your project's Views, Templates and Static
        :param proxyfix:

        """

        if config:
            app.config.from_object(config)

        cls._app = app
        cls.assets = Environment(app)

        app.template_folder = project_dir + "/templates"
        app.static_folder = project_dir + "/static"

        if proxyfix:
            app.wsgi_app = ProxyFix(app.wsgi_app)

        for init_app in cls._init_app_:
            init_app(app)

        for subcls in cls.__subclasses__():
            subcls.register(app)

        @app.after_request
        def after_request(response):
            # Set the cookie on response
            if cls._set_cookie_:
                response.set_cookie(**cls._set_cookie_)
            return response

        @app.context_processor
        def utility_processor():
            """
            Some utility functions that can be used in templates
            """

            def set_page_info(**info):
                cls._UTILITY_PAGE_INFO.update(**info)
                return ""

            def get_page_info(key):
                if key in cls._UTILITY_PAGE_INFO:
                    return cls._UTILITY_PAGE_INFO[key]
                else:
                    return ""

            return dict(set_page_info=set_page_info,
                        get_page_info=get_page_info)
        return app

    @classmethod
    def render(cls, data={}, view_template=None, layout=None, **kwargs):
        """
        To render data to the associate template file of the action view
        :param data: The context data to pass to the template
        :param view_template: The file template to use. By default it will map the module/classname/action.html
        :param layout: The body layout, must contain {% include __view_template__ %}
        """
        if not view_template:
            stack = inspect.stack()[1]
            module = inspect.getmodule(cls).__name__
            module_name = module.split(".")[-1]
            action_name = stack[3]      # The method being called in the class
            view_name = cls.__name__    # The name of the class without View

            if view_name.endswith("View"):
                view_name = view_name[:-4]

            view_template = "%s/%s/%s.html" % (module_name, view_name, action_name)

        if kwargs:
            data.update(kwargs)

        data["__flashed_messages__"] = get_flashed_messages(with_categories=True)
        data["__view_template__"] = view_template

        return render_template(layout or cls.LAYOUT, **data)
