# encoding: utf-8
from __future__ import unicode_literals

import re

from .common import InfoExtractor
from ..utils import compat_urlparse


class SpiegelIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?spiegel\.de/video/[^/]*-(?P<videoID>[0-9]+)(?:\.html)?(?:#.*)?$'
    _TESTS = [{
        'url': 'http://www.spiegel.de/video/vulkan-tungurahua-in-ecuador-ist-wieder-aktiv-video-1259285.html',
        'md5': '2c2754212136f35fb4b19767d242f66e',
        'info_dict': {
            'id': '1259285',
            'ext': 'mp4',
            'title': 'Vulkanausbruch in Ecuador: Der "Feuerschlund" ist wieder aktiv',
            'description': 'md5:8029d8310232196eb235d27575a8b9f4',
            'duration': 49,
        },
    }, {
        'url': 'http://www.spiegel.de/video/schach-wm-videoanalyse-des-fuenften-spiels-video-1309159.html',
        'md5': 'f2cdf638d7aa47654e251e1aee360af1',
        'info_dict': {
            'id': '1309159',
            'ext': 'mp4',
            'title': 'Schach-WM in der Videoanalyse: Carlsen nutzt die Fehlgriffe des Titelverteidigers',
            'description': 'md5:c2322b65e58f385a820c10fa03b2d088',
            'duration': 983,
        },
    }]

    def _real_extract(self, url):
        m = re.match(self._VALID_URL, url)
        video_id = m.group('videoID')

        webpage = self._download_webpage(url, video_id)

        title = self._html_search_regex(
            r'<div class="module-title">(.*?)</div>', webpage, 'title')
        description = self._html_search_meta('description', webpage, 'description')

        base_url = self._search_regex(
            r'var\s+server\s*=\s*"([^"]+)\"', webpage, 'server URL')

        xml_url = base_url + video_id + '.xml'
        idoc = self._download_xml(xml_url, video_id)

        formats = [
            {
                'format_id': n.tag.rpartition('type')[2],
                'url': base_url + n.find('./filename').text,
                'width': int(n.find('./width').text),
                'height': int(n.find('./height').text),
                'abr': int(n.find('./audiobitrate').text),
                'vbr': int(n.find('./videobitrate').text),
                'vcodec': n.find('./codec').text,
                'acodec': 'MP4A',
            }
            for n in list(idoc)
            # Blacklist type 6, it's extremely LQ and not available on the same server
            if n.tag.startswith('type') and n.tag != 'type6'
        ]
        duration = float(idoc[0].findall('./duration')[0].text)

        self._sort_formats(formats)

        return {
            'id': video_id,
            'title': title,
            'description': description,
            'duration': duration,
            'formats': formats,
        }


class SpiegelArticleIE(InfoExtractor):
    _VALID_URL = 'https?://www\.spiegel\.de/(?!video/)[^?#]*?-(?P<id>[0-9]+)\.html'
    IE_NAME = 'Spiegel:Article'
    IE_DESC = 'Articles on spiegel.de'
    _TEST = {
        'url': 'http://www.spiegel.de/sport/sonst/badminton-wm-die-randsportart-soll-populaerer-werden-a-987092.html',
        'info_dict': {
            'id': '1516455',
            'ext': 'mp4',
            'title': 'Faszination Badminton: Nennt es bloß nicht Federball',
            'description': 're:^Patrick Kämnitz gehört.{100,}',
        },
    }

    def _real_extract(self, url):
        m = re.match(self._VALID_URL, url)
        video_id = m.group('id')

        webpage = self._download_webpage(url, video_id)
        video_link = self._search_regex(
            r'<a href="([^"]+)" onclick="return spOpenVideo\(this,', webpage,
            'video page URL')
        video_url = compat_urlparse.urljoin(
            self.http_scheme() + '//spiegel.de/', video_link)

        return {
            '_type': 'url',
            'url': video_url,
        }
