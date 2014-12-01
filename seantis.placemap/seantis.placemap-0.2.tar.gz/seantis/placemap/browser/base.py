from five import grok

from seantis.plonetools.browser import BaseView as SharedBaseView
from seantis.plonetools.browser import BaseForm as SharedBaseForm

from seantis.placemap.interfaces import ISeantisPlacemapSpecific


class BaseView(SharedBaseView):

    grok.baseclass()
    grok.layer(ISeantisPlacemapSpecific)

    domain = 'seantis.placemap'


class BaseForm(SharedBaseForm):

    grok.baseclass()
    grok.layer(ISeantisPlacemapSpecific)

    domain = 'seantis.placemap'
