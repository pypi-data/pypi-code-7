import tornado.web

import data_uri.encoder

class static_file_data_uri_base64(tornado.web.UIModule):
    def render(self, path, force_mimetype='', charset=''):

        self.handler.require_setting("static_path")

        static_file_handler = self.handler.settings.get("static_handler_class", tornado.web.StaticFileHandler)

        abs_path = static_file_handler.get_absolute_path(self.handler.settings['static_path'], path)

        content = open(abs_path).read()

        return data_uri.encoder.EncodeBase64(content, force_mimetype=force_mimetype, charset=charset)
