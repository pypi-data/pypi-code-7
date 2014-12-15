from five import grok

from seantis.plonetools.browser.shared import (
    TranslateMixin,
    StatusMessageMixin
)


class BaseView(grok.View, TranslateMixin, StatusMessageMixin):

    grok.baseclass()
