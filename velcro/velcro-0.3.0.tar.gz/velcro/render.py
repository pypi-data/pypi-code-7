
from html import HtmlRenderer


class Page(object):
    def __init__(self, render_function):
        self.render_function = render_function

    def render_page(self, **kwargs):
        page = HtmlRenderer()
        self.render_function(page, **kwargs)
        return str(page)