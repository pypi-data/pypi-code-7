from zope.interface import Interface
from zope import schema
from zope.i18nmessageid import MessageFactory

_ = MessageFactory(u"plone")


class IMobileThemingSettings(Interface):
    """A theme, loaded from a resource directory
    vocabulary='plone.app.vocabularies.Skins', is for old type skins
    """

    hostnames = schema.Tuple(
        title=_('hostnames', 'Hostnames'),
        description=_('hostnames_description',
                      u'Hostnames to apply the mobile theme'),
        value_type=schema.URI(),
        default=(u'http://localhost:8080',),
        )

    themename = schema.Choice(
        vocabulary='ThemeVocabulary',
        title=_('themename', 'Theme Name'),
        description=_('The name of the mobile theme.'),
        )

    fullurl = schema.Bool(
        title=_('fullurl', 'Redirect to full url'),
        description=_('If set to true, it will redirect site.com/page ' \
                      'to mobilesite/page.'),
        default=False,
        )

    ipad = schema.Bool(
        title=_('ipad', 'Redirect iPads'),
        description=_('Set to false to not redirect on iPad.'),
        default=False,
        )

    tablets = schema.Bool(
        title=_('tablets', 'Redirect Other Tablets'),
        description=_('Set to false to not redirect on other ' \
                      'tablets (Android , BlackBerry, WebOS tablets)'),
        default=False,
        )
