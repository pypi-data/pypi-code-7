import mock

from zope.interface import implementer


from .. import IMixpanelUtility


@implementer(IMixpanelUtility)
class MixpanelTestUtility(mock.Mock):
    pass


def includeme(config):
    utility = MixpanelTestUtility()

    config.registry.registerUtility(utility)
