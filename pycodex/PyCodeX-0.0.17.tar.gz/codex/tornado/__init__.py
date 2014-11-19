from .template import Loader, append_template_suffix

import codex.tornado.helpers
import tornado.websocket
import tornado.options
import tornado.ioloop
import tornado.escape
import tornado.web
import http.client
import functools
import traceback
import importlib
import sys
import os

class Application(tornado.web.Application):

    def __init__(self, handlers, app_settings):

        settings = app_settings.config

        for arg_value in sys.argv:
            if arg_value.find('--port=') == 0:
                self.port = arg_value.replace('--port=', '', 1).strip()

        if not hasattr(self, 'port'):
            if 'default_port' in settings:
                self.port = settings['default_port']
            else:
                self.port = 80

        cli_args = [sys.argv[0]]
        self.root_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

        if 'enable_logs' in settings and settings['enable_logs'] and 'log_path' in settings and settings['log_path']:
            settings['log_path'] = self.root_dir + '/' + settings['log_path'].strip('/') + '/'
            if not os.path.exists(settings['log_path']):
                os.mkdir(settings['log_path'])
            cli_args.append('--log_file_prefix=' + settings['log_path'] + 'port-' + str(self.port) + '.log')   

        if 'template_path' in settings:
            settings['template_path'] = self.root_dir + '/' + settings['template_path'].lstrip('/')

        if 'template_suffix' not in settings:
            settings['template_suffix'] = 'html'

        template_args = {}
        if 'autoescape' in settings:
            template_args['autoescape'] = settings['autoescape']
        settings['template_loader'] = Loader(settings['template_path'], **template_args)
        settings['template_loader'].set_template_suffix(settings['template_suffix'])

        if 'static_path' in settings:
            settings['static_path'] = self.root_dir + '/' + settings['static_path'].lstrip('/')

        if 'ui_methods' in settings:
            if isinstance(settings['ui_methods'], list):
                for i, ui_method in enumerate(settings['ui_methods']):
                    if isinstance(ui_method, str):
                        settings['ui_methods'][i] = __import__('app.helpers.' + ui_method)
                settings['ui_methods'].append(codex.tornado.helpers)
            else:
                raise Exception('ui_methods config must be a list')
        else:
            settings['ui_methods'] = [codex.tornado.helpers]

        if len(cli_args) > 1:
            tornado.options.parse_command_line(cli_args)

        super().__init__(handlers, **settings)

    def get_ioloop_instance(self):
        return tornado.ioloop.IOLoop.instance()
        
    def run(self):
        self.listen(self.port)
        self.get_ioloop_instance().start()

class ViewData(object):
    def __init__(self):
        self.__dict__['data'] = {}

    def __getattr__(self, name):
        return self.__dict__['data'].get(name)

    def __setattr__(self, name, value):
        self.__dict__['data'][name] = value

    def merge(self, data):
        self.__dict__['data'].update(data)
        return self

    def all(self):
        return self.__dict__['data']

class URI:
    def __init__(self, request_path):
        if request_path[0] == '/':
            request_path = request_path[1:]
        self.path = request_path
        self.segments = self.path.split('/')

    def segment(self, index, default=None):
        if index < 1:
            return None
        index -= 1
        if index >= len(self.segments):
            return default
        return self.segments[index]
        
class Controller(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        self._setup(application, request)
        super().__init__(application, request, **kwargs)
        self.disable_cache()

    def _setup(self, application, request, with_session=True):
        
        self.view = ViewData()
        self.request = request
        self.application = application

        if not hasattr(self, 'uri'):
            self.uri = URI(self.request.path)
        
    def disable_cache(self):
        self.set_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.set_header('Pragma', 'no-cache')
        self.set_header('Expires', '0')

    def write_error(self, status_code, **kwargs):
        kwargs['code'] = status_code
        if 'exc_info' in kwargs:
            if self.settings.get('serve_traceback'):
                kwargs['message'] = '<pre>' + ''.join(traceback.format_exception(*kwargs['exc_info'])) + '</pre>'
            else:
                kwargs['message'] = kwargs['exc_info'][1]
        elif hasattr(self, '_reason'):
            kwargs['message'] = self._reason
        else:
            kwargs['message'] = http.client.responses[status_code]

        self.render('errors/' + str(status_code) + '.html', **kwargs)

    def get_argument(self, name, default=None, strip=True, xss_filter=None):
        return self._get_argument(name, default, self.request.arguments, strip, xss_filter)

    def get_query_argument(self, name, default=None, strip=True, xss_filter=None):
        return self._get_argument(name, default, self.request.query_arguments, strip, xss_filter)

    def get_body_argument(self, name, default=None, strip=True, xss_filter=None):
        return self._get_argument(name, default, self.request.body_arguments, strip, xss_filter)

    def _get_argument(self, name, default, source, strip=True, xss_filter=None):
        val = super()._get_argument(name, default, source, strip)
        if val and (xss_filter == True or (xss_filter is None and self.settings.get('global_xss_filtering'))):
            return tornado.escape.xhtml_escape(val)
        return val

    def get_arguments(self, name, strip=True, xss_filter=None):
        return self._get_arguments(name, self.request.arguments, strip, xss_filter)

    def get_query_arguments(self, name, strip=True, xss_filter=None):
        return self._get_arguments(name, self.request.query_arguments, strip, xss_filter)

    def get_body_arguments(self, name, strip=True, xss_filter=None):
        return self._get_arguments(name, self.request.body_arguments, strip, xss_filter)

    def _get_arguments(self, name, source, strip=True, xss_filter=None):
        values = super()._get_arguments(name, source, strip)
        if values and (xss_filter == True or (xss_filter is None and self.settings.get('global_xss_filtering'))):
            for k, v in enumerate(values):
                if v:
                    values[k] = tornado.escape.xhtml_escape(v)
        return values

    @property
    def root_dir(self):
        return self.application.root_dir

    def view_exists(self, path):
        return os.path.exists(self.root_dir + '/app/views' + (('/' + path.lstrip('/')).rstrip('.') + '.') + self.settings.get('template_suffix'))

    def render_string(self, template_name, **kwargs):
        template_name = append_template_suffix(template_name, self.settings.get('template_suffix'))
        view_data = self.view.all()
        view_data.update(kwargs)
        view_data['settings'] = self.settings
        if hasattr(self, 'uri'):
            view_data['uri'] = self.uri
        return super().render_string(template_name, **view_data)

    def flash_cookie(self, name):
        value = self.get_cookie(name)
        if value is not None:
            self.clear_cookie(name)
        return value

    def flash_secure_cookie(self, name):
        value = self.get_secure_cookie(name)
        if value is not None:
            self.clear_cookie(name)
        return value

    def finish(self, chunk=None):
        super().finish(chunk)

    def get_unauthenticated_url(self):
        return self.settings.get('unauthenticated_url')

class WebSocketController(tornado.websocket.WebSocketHandler, Controller):
    def __init__(self, application, request, **kwargs):
        self._setup(application, request, False)
        super().__init__(application, request, **kwargs)

    def on_connection_close(self):
        super().on_connection_close()
        self.dispose_resources()

for method in ["disable_cache", "flash_cookie", "flash_secure_cookie", "load_session"]:
    setattr(WebSocketController, method, tornado.websocket._wrap_method(getattr(WebSocketController, method)))

authenticated = tornado.web.authenticated

def unauthenticated(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.current_user:
            url = self.get_unauthenticated_url()
            if url:
                self.redirect(url)
                return
            raise tornado.web.HTTPError(403)
        return method(self, *args, **kwargs)
    return wrapper

class Error(Controller):
    def __init__(self, application, request, status_code):
        super().__init__(application, request)
        self.set_status(status_code)
    
    def prepare(self):
        raise tornado.web.HTTPError(self._status_code)
 
tornado.web.ErrorHandler = Error