from flask import request, url_for, redirect
import flask
from flask.ext.debugtoolbar import DebugToolbarExtension


def current_for(**values):
    return url_for(endpoint=request.endpoint, **values)


def redirect_for(endpoint, **values):
    return redirect(url_for(endpoint=endpoint, **values))


class Request(flask.Request):
    @property
    def is_get(self):
        return self.method == 'GET'

    @property
    def is_post(self):
        return self.method == 'POST'


class Glask(flask.Flask):
    def __init__(self, import_name, static_path=None, static_url_path=None,
                 static_folder='static', template_folder='templates',
                 instance_path=None, instance_relative_config=False):
        super(Glask, self).__init__(import_name, static_path, static_url_path,
                                    static_folder, template_folder,
                                    instance_path, instance_relative_config)
        self.jinja_env.globals.update(current_for=current_for)
        self.request_class = Request
        _config_from_object = self.config.from_object

        def config_from_object(object):
            _config_from_object(object)
            self.init_after_config()

        self.config.from_object = config_from_object

    def init_after_config(self):
        if self.debug:
            DebugToolbarExtension(self)
