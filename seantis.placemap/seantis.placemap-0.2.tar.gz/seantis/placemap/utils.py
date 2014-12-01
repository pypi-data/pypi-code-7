import fastkml
import logging
import lxml
import re
import requests

from seantis.placemap import _
from seantis.plonetools import tools


log = logging.getLogger('seantis.placemap')


def translate_kml_document(request, document):
    # collective.geo.kml doesn't correctly translate strings in KML, so we
    # do it here to work around this issue.

    translate = tools.translator(request, 'seantis.placemap')
    translation = translate(_(u"See the original resource"))

    return document.replace(u"See the original resource", translation)


fixes = [
    (re.compile(r'type="xsd:([a-z]+)"'), 'type="\g<1>"')
]


def fix_common_kml_problems(content):
    for expression, substitute in fixes:
        content = expression.sub(substitute, content)

    return content


def fetch_kml_document(url):

    candidates = (url, url + '/@@kml-document')

    for url in candidates:
        try:
            response = requests.get(url)
        except requests.exceptions.RequestException:
            continue

        if response.status_code != 200:
            continue

        try:
            # fix common problems with kml
            fastkml.kml.KML().from_string(
                fix_common_kml_problems(response.content)
            )
        except (lxml.etree.XMLSyntaxError, TypeError):
            log.exception("Error parsing KML")
            continue
        else:
            return response.content.decode('utf-8')

    return None
