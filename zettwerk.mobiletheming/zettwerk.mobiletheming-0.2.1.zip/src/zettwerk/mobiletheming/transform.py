from plone.app.theming.transform import ThemeTransform

from zope.component import queryUtility
from zope.component import getUtility

from plone.app.theming.interfaces import IThemeSettings
from plone.app.theming.utils import getAvailableThemes

from plone.app.theming.utils import compileThemeTransform
from plone.app.theming.utils import prepareThemeParameters
from plone.app.theming.utils import findContext
from plone.app.theming.transform import _Cache

from plone.registry.interfaces import IRegistry


class MobileThemeTransform(ThemeTransform):

    order = 8850

    def _getActive(self):
        """ check if the mobile theming for this url is active """

        active = False
        registry = getUtility(IRegistry)

        base1 = self.request.get('BASE1')
        _xx_, base1 = base1.split('://', 1)
        host = base1.lower()

        hostnames = registry[
            'zettwerk.mobiletheming.interfaces.IMobileThemingSettings' \
                '.hostnames'
        ]
        if hostnames:
            for hostname in hostnames or ():
                if host == hostname or \
                   hostname == "http://%s" % (host):
                    active = True

        return active

    def transformIterable(self, result, encoding):
        """Apply the transform if required
        """
        active = self._getActive()

        registry = getUtility(IRegistry)
        themename = registry[
            'zettwerk.mobiletheming.interfaces.IMobileThemingSettings' \
                '.themename'
        ]

        availableThemes = getAvailableThemes()
        mobile = None
        for item in availableThemes:
            if item.__name__ == themename:
                mobile = item
                active = active and True

        if not active or mobile is None:
            ## return the default theme
            result = super(MobileThemeTransform, self) \
                .transformIterable(result, encoding)
            return result

        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IThemeSettings, False)

        class S(object):
            rules = mobile.rules

            doctype = settings.doctype
            absolutePrefix = settings.absolutePrefix
            readNetwork = settings.readNetwork
            parameterExpressions = settings.parameterExpressions

        fake_settings = S()

        return self.transformIterableWithSettings(result, encoding,
                                                  fake_settings)

    def transformIterableWithSettings(self, result, encoding, settings):
        """ """
        result = self.parseTree(result)
        if result is None:
            return None

        if settings.doctype:
            result.doctype = settings.doctype
            if not result.doctype.endswith('\n'):
                result.doctype += '\n'

        transform = compileThemeTransform(settings.rules,
                                          settings.absolutePrefix,
                                          settings.readNetwork,
                                          settings.parameterExpressions)
        if transform is None:
            return None

        cache = _Cache()
        parameterExpressions = settings.parameterExpressions or {}
        params = prepareThemeParameters(findContext(self.request),
                                        self.request,
                                        parameterExpressions,
                                        cache)

        transformed = transform(result.tree, **params)
        if transformed is not None:
            # Transformed worked, swap content with result
            result.tree = transformed

        return result
