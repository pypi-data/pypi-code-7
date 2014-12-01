# -*- coding: utf-8 -*-

from urlparse import urlparse
from redturtle.video.browser.videoembedcode import VideoEmbedCode
try:
    from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
except ImportError:
    # Plone < 4.1
    from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile


class VimeoEmbedCode(VideoEmbedCode):
    """ VimeoEmbedCode 
    provides a way to have a html code to embed Vimeo video in a web page 

    >>> from zope.interface import implements
    >>> from redturtle.video.interfaces import IRTRemoteVideo
    >>> from redturtle.video.interfaces import IVideoEmbedCode
    >>> from zope.component import getMultiAdapter
    >>> from redturtle.video.tests.base import TestRequest

    >>> class RemoteVideo(object):
    ...     implements(IRTRemoteVideo)
    ...     remoteUrl = 'http://vimeo.com/2075738'
    ...     size = {'width': 400, 'height': 225}
    ...     def getRemoteUrl(self):
    ...         return self.remoteUrl
    ...     def getWidth(self):
    ...         return self.size['width']
    ...     def getHeight(self):
    ...         return self.size['height']

    >>> remotevideo = RemoteVideo()
    >>> request = TestRequest()
    >>> request.QUERY_STRING = ''
    >>> adapter = getMultiAdapter((remotevideo, request), 
    ...                                         IVideoEmbedCode, 
    ...                                         name = 'vimeo.com')
    >>> adapter.getVideoLink()
    'https://player.vimeo.com/video/2075738'

    >>> print adapter()
    <div class="vimeoEmbedWrapper">
    <iframe width="400" height="225" frameborder="0"
            webkitallowfullscreen="webkitallowfullscreen"
            mozallowfullscreen="mozallowfullscreen"
            allowfullscreen="allowfullscreen"
            src="https://player.vimeo.com/video/2075738">
    </iframe>
    </div>
    <BLANKLINE>

    Now check if the autoplay parameter is used when putted into the video source URL.

    >>> remotevideo.remoteUrl += '?autoplay=1'
    >>> print adapter()
    <div class="vimeoEmbedWrapper">
    <iframe width="400" height="225" frameborder="0"
            webkitallowfullscreen="webkitallowfullscreen"
            mozallowfullscreen="mozallowfullscreen"
            allowfullscreen="allowfullscreen"
            src="https://player.vimeo.com/video/2075738?autoplay=1">
    </iframe>
    </div>
    <BLANKLINE>

    If the request URL is provided with a "autoplay=1" parameter, autoplay is included

    >>> remotevideo.remoteUrl = 'http://vimeo.com/2075738'
    >>> request.QUERY_STRING = '?foo=5&autoplay=1&bar=7'
    >>> print adapter()
    <div class="vimeoEmbedWrapper">
    <iframe width="400" height="225" frameborder="0"
            webkitallowfullscreen="webkitallowfullscreen"
            mozallowfullscreen="mozallowfullscreen"
            allowfullscreen="allowfullscreen"
            src="https://player.vimeo.com/video/2075738?autoplay=1">
    </iframe>
    </div>
    <BLANKLINE>

    """
    template = ViewPageTemplateFile('vimeoembedcode_template.pt')

    def getVideoLink(self):
        video_id = urlparse(self.context.getRemoteUrl())[2][1:]
        video_url = "https://player.vimeo.com/video/%s" % video_id
        return self.check_autoplay(video_url)

    def check_autoplay(self, url):
        """Check if the we need to add the autoplay parameter, and add it to the URL"""
        if self.context.getRemoteUrl().lower().find('autoplay=1')>-1 or \
                self.request.QUERY_STRING.lower().find('autoplay=1')>-1:
            url += '?autoplay=1'
        return url
