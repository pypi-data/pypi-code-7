from html.parser import HTMLParser

__all__ = ['HTMLMetaParser']


class HTMLMetaParser(HTMLParser):
    def __init__(self):
        super(HTMLMetaParser, self).__init__()
        self._is_title = False

        self.description = self.og_description = None
        self.image_url = self.og_image_url = None

    def handle_starttag(self, tag, attrs):
        if tag == 'title':
            self._is_title = True
        elif tag == 'img' and self.image_url is None:
            attrs = dict(attrs)
            self.image_url = attrs.get('src')
        elif tag == 'meta':
            attrs = dict(attrs)
            if attrs.get('property') == 'og:image':
                self.og_image_url = attrs.get('content')
            elif attrs.get('property') == 'og:description':
                self.og_description = attrs.get('content')
            elif attrs.get('name') == 'description':
                self.description = attrs.get('content')

    def handle_data(self, data):
        if self._is_title:
            self.title = data

    def handle_endtag(self, tag):
        self._is_title = False
