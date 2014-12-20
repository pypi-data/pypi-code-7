from flask import Blueprint
from .renderer import render_field, csrf_setup
from .filters import (
    timesince,
    local_date,
    percent_escape,
    local_date_time,
    get_autoincluded_assets
)
class Boilerplate(object):

    def __init__(self, app=None, **kwargs):
        self.app = app

        if app is not None:
            self._state = self.init_app(app, **kwargs)

    def init_app(self, app):
        bp = Blueprint(
            'boilerplate',
            __name__,
            template_folder='templates',
            url_prefix='/bp'
        )

        app.register_blueprint(bp)

        app.jinja_env.globals['csrf_setup'] = csrf_setup
        app.jinja_env.globals['render_field'] = render_field
        app.jinja_env.globals['html_assets'] = get_autoincluded_assets(app)()
        app.jinja_env.filters['local_date'] = local_date
        app.jinja_env.filters['local_date_time'] = local_date_time
        app.jinja_env.filters['percent_escape'] = percent_escape
        app.jinja_env.filters['time_since'] = timesince
