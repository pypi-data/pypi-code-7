import logging
import sys

from AccessControl import getSecurityManager
from Acquisition import aq_acquire
from ZODB.POSException import ConflictError

from Products.CMFCore.permissions import ModifyPortalContent
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets import ViewletBase

from collective.portlet.pythonscript.browser.portlet import PythonScriptPortletRenderer

logger = logging.getLogger('pythonscript.viewlet')


class PythonScriptViewletSettingsDescriptor(object):

    def __init__(self, label):
        self.label = label

    def __get__(self, instance, owner):
        try:
            context = instance.context
            value = context.Schema().get(self.label).get(context)
        except AttributeError:
            return None

        if isinstance(value, unicode):
            value = value.encode('utf-8')
        return value


class PythonScriptViewlet(ViewletBase, PythonScriptPortletRenderer):
    """ Viewlet for displaying the python script results """

    index = ViewPageTemplateFile("pythonscript-viewlet.pt")
    error_template = ViewPageTemplateFile("pythonscript-error.pt")
    error_message = "<!-- Unable to render pyhtonscript vielet content -->"
    viewlet_title = PythonScriptViewletSettingsDescriptor('viewlet_title')
    template_name = PythonScriptViewletSettingsDescriptor('template_name')
    script_name = PythonScriptViewletSettingsDescriptor('script_name')
    limit_results = PythonScriptViewletSettingsDescriptor('limit_results')

    def __init__(self, context, request, view, manager=None):
        super(PythonScriptViewlet, self).__init__(context, request, view, manager=None)

    @property
    def data(self):
        return self

    def display(self):
        return self.script_name and self.template_name

    def safe_render(self):
        try:
            return self.renderResults()
        except ConflictError:
            raise
        except Exception:
            logger.exception('Error while rendering %r' % self)
            aq_acquire(self.context, 'error_log').raising(sys.exc_info())
            if getSecurityManager().checkPermission(ModifyPortalContent, self.context):
                return self.error_template()
            return self.error_message
