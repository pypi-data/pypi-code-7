from lxml import html, etree
from parslepy import Parselet
from parslepy.funcs import xpathstrip, xpathtostring
from cssselect import HTMLTranslator
import re


ns = etree.FunctionNamespace(None)
ns['strip'] = xpathstrip
ns['str'] = xpathtostring


def extract_urls(self, xpath=None):
    urlpattern = re.compile(
        r'^(?:http)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    if xpath and not xpath.endswith('/'):
        xpath += '/'
    elif xpath is None:
        xpath = ""
    return set(url for url in self.xpath(xpath + "descendant-or-self::a/@href")
               if urlpattern.match(url))


def extract_text(self):
    return "".join(i.strip() for i in self.itertext())


def extract(self, rules, strict=False):
    parselet = Parselet(rules, strict=strict)
    return parselet.extract(self)


def cssselect(self, expr):
    return self._css_translator.css_to_xpath(expr)


def css(self, expr):
    return self.xpath(self.cssselect(expr))


def html_content(self, pretty_print=False):
    return html.tostring(self, pretty_print, encoding='utf-8')


html.HtmlElement.extract_text = extract_text
html.HtmlElement._css_translator = HTMLTranslator()
html.HtmlElement.cssselect = cssselect
html.HtmlElement.css = css
html.HtmlElement.extract = extract
html.HtmlElement.extract_urls = extract_urls
html.HtmlElement.html = html_content


def HtmlParser(response, absolute_links=True):
    """
    :param response:
    :type response: :class:`dragline.http.Response`

    This method takes response object as its argument and returns
    the lxml etree object.

    HtmlParser function returns a lxml object of type HtmlElement which got few potential methods.
    All the details of lxml object are discussed in section `lxml.html.HtmlElement`.
    """
    parser = html.HTMLParser(recover=True, encoding='utf-8')
    if isinstance(response, basestring):
        element = html.fromstring(response, None, parser)
    else:
        element = html.fromstring(response.content, response.url, parser)
        if absolute_links:
            element.make_links_absolute()
    return element
