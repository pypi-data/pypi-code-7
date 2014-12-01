# -*- coding: utf-8 -*-

from urlparse import urlparse
from redturtle.video.remote_thumb import RemoteThumb
from redturtle.video.browser.videoembedcode import VideoEmbedCode
try:
    from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
except ImportError:
    # Plone < 4.1
    from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile


class YoutubeBase(object):

    def getThumb(self):
        """
        Youtube API 2.0 use this format to return images:
        https://img.youtube.com/vi/<video id>/{0,1,2,3}.jpg;

        video id: an alphanumeric string like 'ODA33daiSS';
        image format: always 'jpg', so we use a fix 'image/jpeg' as mimetype;
        {0,1,2,3}: youtube should provide 4 thumb. The first one (0) is the
                   biggest one; the others are smaller, so we take the biggest.

        So you can call somethign like:
             https://img.youtube.com/vi/S9UABZVATeY/0.jpg
        """
        parsed_remote_url = urlparse(self.context.getRemoteUrl())
        video_id = self.get_video_id(parsed_remote_url)
        img_url = 'https://img.youtube.com/vi/%s/0.jpg' % video_id
        thumb_obj = RemoteThumb(img_url,
                                'image/jpeg',
                                '%s-image.jpg' % video_id)
        return thumb_obj

    def check_autoplay(self, url):
        """Check if the we need to add the autoplay parameter, and add it to the URL"""
        if self.context.getRemoteUrl().lower().find('autoplay=1')>-1 or \
                self.request.QUERY_STRING.lower().find('autoplay=1')>-1:
            url += '?autoplay=1&enablejsapi=1'
        return url

    def check_autofocus(self):
        """If the autoplay parameter is in the URL, return True (for enabling autofocus)"""
        return self.request.QUERY_STRING.lower().find('autoplay=1')>-1


class ClassicYoutubeEmbedCode(YoutubeBase, VideoEmbedCode):
    """ClassicYoutubeEmbedCode
    Provides a way to have a html code to embed Youtube video in a web page

    >>> from zope.interface import implements
    >>> from redturtle.video.interfaces import IRTRemoteVideo
    >>> from redturtle.video.interfaces import IVideoEmbedCode
    >>> from zope.component import getMultiAdapter
    >>> from collective.rtvideo.youtube.tests.base import TestRequest

    >>> request = TestRequest()

    >>> class RemoteVideo(object):
    ...     implements(IRTRemoteVideo)
    ...     remoteUrl = 'https://www.youtube.com/watch?v=s43WGi_QZEE&feature=related'
    ...     size = {'width': 425, 'height': 349}
    ...     def getRemoteUrl(self):
    ...         return self.remoteUrl
    ...     def getWidth(self):
    ...         return self.size['width']
    ...     def getHeight(self):
    ...         return self.size['height']

    >>> remotevideo = RemoteVideo()
    >>> adapter = getMultiAdapter((remotevideo, request),
    ...                                         IVideoEmbedCode,
    ...                                         name = 'youtube.com')
    >>> adapter.getVideoLink()
    'https://www.youtube.com/embed/s43WGi_QZEE'

    >>> print adapter()
    <div class="youtubeEmbedWrapper">
    <BLANKLINE>
    <iframe width="425"
            height="349"
            frameborder="0"
            allowfullscreen
            src="https://www.youtube.com/embed/s43WGi_QZEE">
    </iframe>
    </div>
    <BLANKLINE>

    Now check if the autoplay parameter is used when putted into the video source URL.

    >>> remotevideo.remoteUrl += '?AUTOPLAY=1'
    >>> print adapter()
    <div class="youtubeEmbedWrapper">
    <iframe width="425"
            height="349"
            frameborder="0"
            allowfullscreen
            src="https://www.youtube.com/embed/s43WGi_QZEE?autoplay=1&amp;enablejsapi=1">
    </iframe>
    </div>
    <BLANKLINE>

    If the request URL is provided with a "autoplay=1" parameter, autoplay and accessibility/usability
    tricks are included

    >>> request.QUERY_STRING = '?foo=5&autoplay=1&bar=7'
    >>> print adapter()
    <div class="youtubeEmbedWrapper">
    <script type="text/javascript">
    <!--
    function onYouTubePlayerReady() {
        document.getElementById('youtubeVideo').focus();
    }
    //-->
    </script>
    <iframe width="425"
            height="349"
            frameborder="0"
            allowfullscreen
            src="https://www.youtube.com/embed/s43WGi_QZEE?autoplay=1&amp;enablejsapi=1"
            tabindex="1">
    </iframe>
    </div>
    <BLANKLINE>

    """
    template = ViewPageTemplateFile('youtubeembedcode_template.pt')

    def getVideoLink(self):
        qs = urlparse(self.context.getRemoteUrl())[4]
        params = qs.split('&')
        for param in params:
            k, v = param.split('=')
            if k == 'v':
                return self.check_autoplay('https://www.youtube.com/embed/%s' % v)

    def getEmbedVideoLink(self):
        """Video link, just for embedding needs"""
        return self.getVideoLink()

    def get_video_id(self, parsed_remote_url):
        qs = parsed_remote_url[4]
        return dict([x.split("=") for x in qs.split("&")])['v']


class ShortYoutubeEmbedCode(YoutubeBase, VideoEmbedCode):
    """ ShortYoutubeEmbedCode
    Provides a way to have a html code to embed Youtube video in a web page (short way).
    Also, the new version of the embed URL must works:

    >>> from zope.interface import implements
    >>> from redturtle.video.interfaces import IRTRemoteVideo
    >>> from redturtle.video.interfaces import IVideoEmbedCode
    >>> from zope.component import getMultiAdapter
    >>> from collective.rtvideo.youtube.tests.base import TestRequest

    >>> class RemoteVideo(object):
    ...     implements(IRTRemoteVideo)
    ...     remoteUrl = 'https://youtu.be/s43WGi_QZEE'
    ...     size = {'width': 425, 'height': 349}
    ...     def getRemoteUrl(self):
    ...         return self.remoteUrl
    ...     def getWidth(self):
    ...         return self.size['width']
    ...     def getHeight(self):
    ...         return self.size['height']

    >>> remotevideo = RemoteVideo()
    >>> adapter = getMultiAdapter((remotevideo, TestRequest()),
    ...                                         IVideoEmbedCode,
    ...                                         name = 'youtu.be')
    >>> adapter.getVideoLink()
    'https://youtu.be/s43WGi_QZEE'

    >>> print adapter()
    <div class="youtubeEmbedWrapper">
    <BLANKLINE>
    <iframe width="425"
            height="349"
            frameborder="0"
            allowfullscreen
            src="https://www.youtube.com/embed/s43WGi_QZEE">
    </iframe>
    </div>
    <BLANKLINE>

    """
    template = ViewPageTemplateFile('youtubeembedcode_template.pt')

    def getEmbedVideoLink(self):
        """Video link to be used for play video, so in the extended format"""
        path = urlparse(self.context.getRemoteUrl())[2]
        return self.check_autoplay('https://www.youtube.com/embed%s' % path)

    def getVideoLink(self):
        path = urlparse(self.context.getRemoteUrl())[2]
        return self.check_autoplay('https://youtu.be%s' % path)

    def get_video_id(self, parsed_remote_url):
        return parsed_remote_url[2].replace('/', '')
