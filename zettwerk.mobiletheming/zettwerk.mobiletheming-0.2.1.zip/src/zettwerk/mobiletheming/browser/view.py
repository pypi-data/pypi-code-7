from Products.Five.browser import BrowserView
from zope.component import getUtility
from zope.component import getMultiAdapter
from plone.registry.interfaces import IRegistry
from urlparse import urlparse


class MobRedirected(BrowserView):

    def __call__(self, request=None, ref='', url=''):
        """ Sends the user to the same page they were at before going to mobile
        site."""
        refpage = urlparse(url)
        redirect_to = refpage.path
        if refpage.query:
            redirect_to += ('?' + refpage.query)

        return self.context.REQUEST.RESPONSE.redirect(redirect_to)


class JavaScript(BrowserView):

    def __call__(self, request=None, response=None):
        """Returns configurations."""
        self.registry = getUtility(IRegistry)
        self.request.response.setHeader("Content-type", "text/javascript")

        ## only return the redirect stuff, if the mobile theming
        ## is _not_ active for this url
        active = getMultiAdapter((request.get('PUBLISHED', None), request),
                                 name='zettwerk_mobiletheming_transform') \
            ._getActive()

        hostname = self.hostname
        force_path_and_query = ''

        if self.fullurl and not active:
            force_path_and_query += '/@@mobredirected/?url='
            ref = urlparse(self.request.get_header("referer"))
            force_path_and_query += ref.path

            if ref.query:
                force_path_and_query += '?'
                force_path_and_query += ref.query

        if not active and hostname:
            script_url = '/++resource++zettwerk.mobiletheming.scripts' \
                         '/me.redirect.min.js'
            return """\
            var mobile_domain = "%(hostname)s";
            var ipad = "%(ipad)s";
            var other_tablets = "%(tablets)s";
            var force_path_and_query = "%(force_path_and_query)s";
            document.write(unescape("%%3Cscript """ \
                """ src='%(script_url)s' """ \
                """ type='text/javascript'%%3E%""" \
                """%3C/script%%3E"));""" % {
                    'hostname': hostname,
                    'ipad': self.ipad,
                    'tablets': self.tablets,
                    'force_path_and_query': force_path_and_query,
                    'script_url': script_url,
                }
        return ''

    @property
    def hostname(self):
        registry = getUtility(IRegistry)
        hostnames = registry[
            'zettwerk.mobiletheming.interfaces.IMobileThemingSettings' \
                '.hostnames'
        ]

        if not hostnames:
            return ''

        first = hostnames[0]
        parts = urlparse(first)

        ## two cases:
        ## 1. no rewritten url with port and plone instance
        ## 2. rewritten url without plone instance
        ## for both cases, no protocol (http/s) is needed
        if parts.port:
            ## there is a port, so append the portal id
            return '%s:%s/%s' % (
                parts.hostname,
                parts.port,
                self.context.portal_url.getPortalObject().getId()
            )
        else:
            return parts.hostname

    @property
    def tablets(self):
        return self.registry[
            'zettwerk.mobiletheming.interfaces.IMobileThemingSettings' \
                '.tablets']

    @property
    def ipad(self):
        return self.registry[
            'zettwerk.mobiletheming.interfaces.IMobileThemingSettings' \
                '.ipad']

    @property
    def fullurl(self):
        return self.registry[
            'zettwerk.mobiletheming.interfaces.IMobileThemingSettings' \
                '.fullurl']
