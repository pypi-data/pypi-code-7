
class Model(object):
    def __init__(self, html_renderer, **attrs):
        self.attrs = attrs
        self.page = html_renderer

    def pre_context(self):
        pass

    def post_context(self):
        pass

    def no_context(self):
        pass

    def __enter__(self):
        self.pre_context()
        return self

    def __exit__(self, *args):
        self.post_context()

    def __call__(self):
        self.no_context()