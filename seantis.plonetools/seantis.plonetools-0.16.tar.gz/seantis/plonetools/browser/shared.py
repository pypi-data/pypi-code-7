from Products.statusmessages.interfaces import IStatusMessage
from seantis.plonetools import tools


class TranslateMixin(object):
    """ Shared by BaseView and BaseForm. """

    @property
    def domain(self):
        """ The translation domain. """
        raise NotImplementedError

    def translate(self, text, domain=None):
        return tools.translator(self.request, domain or self.domain)(text)


class StatusMessageMixin(object):

    def message(self, message, type="info"):
        IStatusMessage(self.request).add(message, type)
