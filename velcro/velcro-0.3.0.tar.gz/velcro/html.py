
def format_attribute_dictionary(attr_dict):
    return {attr.replace('klass', 'class').replace('_', '-'): val for attr, val in attr_dict.iteritems()}


class HtmlNode(object):
    def __init__(self, element, page):
        self._element = element
        self._page = page
        self._attrs = {}

    @staticmethod
    def format_html_attribute_dictionary(attr_dict):
        attrs = ['{}="{}"'.format(attr, val) for attr, val in format_attribute_dictionary(attr_dict).iteritems()]
        return (' ' + ' '.join(attrs)) if attrs else ''

    def __call__(self, **attrs):
        self._attrs = attrs
        return self

    def __enter__(self):
        self._page.text('<{}{}>'.format(self._element, HtmlNode.format_html_attribute_dictionary(self._attrs)))
        self._page.indent += 1

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            with self._page.div:
                with self._page.h3:
                    self._page.text(exc_type)
                with self._page.p:
                    self._page.text(exc_val)
                with self._page.code:
                    self._page.text(exc_tb)
        self._page.indent -= 1
        self._page.text('</{}>'.format(self._element))

    def empty(self):
        with self:
            pass


class CssStyle(object):
    IN_STYLE = 1
    MID_RULE = 2

    def __init__(self, page):
        self._page = page
        self._state = None

    @staticmethod
    def format_css_attribute_dictionary(attr_dict):
        return ('{' +
                ''.join(['{}:{};'.format(attr, val)
                         for attr, val
                         in format_attribute_dictionary(attr_dict).iteritems()]) +
                '}')

    def __enter__(self):
        if self._state is not None:
            raise SyntaxError('You cannot open a style within itself.')
        self._page.text('<style>')
        self._page.indent += 1
        self._state = self.IN_STYLE
        return self

    def __exit__(self, *_):
        if self._state is self.MID_RULE:
            raise SyntaxError('You cannot leave a style mid-rule.')
        self._state = None
        self._page.indent -= 1
        self._page.text('</style>')

    def on(self, *selectors):
        if self._state is not self.IN_STYLE:
            raise SyntaxError('Not the proper place.')
        self._page.text(','.join(selectors))
        self._state = self.MID_RULE
        return self

    def apply(self, **rules):
        if self._state is not self.MID_RULE:
            raise SyntaxError('Not the proper place.')
        self._page.text(CssStyle.format_css_attribute_dictionary(rules))
        self._state = self.IN_STYLE


class HtmlRenderer(object):
    def __init__(self, doctype='<!doctype html>'):
        self._buffer = doctype + '\n'
        self.indent = 0

    def text(self, txt, break_line=True):
        self._buffer += "{indentation}{content}".format(indentation=('\t' * self.indent), content=txt)
        if break_line:
            self._buffer += '\n'

    def node(self, element, **attrs):
        self.text('<{}{}>'.format(element, HtmlNode.format_html_attribute_dictionary(attrs)))

    @property
    def style(self):
        return CssStyle(self)

    def __getattr__(self, element):
        return HtmlNode(element, self)

    def __str__(self):
        return self._buffer