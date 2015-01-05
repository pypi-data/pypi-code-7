from OFS.SimpleItem import SimpleItem
from zope.component import adapts
from zope.interface import Interface, implements
from zope.formlib import form
from zope import schema
from zope.security.untrustedpython.interpreter import CompiledProgram
from plone.memoize.instance import memoize

from plone.app.contentrules.browser.formhelper import AddForm, EditForm
from plone.contentrules.rule.interfaces import IRuleElementData, IExecutable

from zope.i18n import MessageFactory


_ = MessageFactory('collective.ruleactions.pythonscript')


class IPythonScriptAction(Interface):
    script = schema.Text(
        title=_(u"Script"),
        description=_(u"")
    )


class PythonScriptAction(SimpleItem):
    """The implementation of the action
    """
    implements(IPythonScriptAction, IRuleElementData)

    script = ''

    element = 'collective.ruleactions.pythonscript'

    summary = 'Run python script'


class PythonScriptExecutor(object):
    """The executor for this action.
    """
    implements(IExecutable)
    adapts(Interface, IPythonScriptAction, Interface)

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    @memoize
    def _script(self, code):
        return CompiledProgram(code)

    @property
    def script(self):
        return self._script(self.element.script)

    def __call__(self):
        return self.script.exec_({'context': self.context,
                                  'event': self.event})


class PythonScriptAddForm(AddForm):
    """
    An add form for the pythonscript action
    """
    form_fields = form.FormFields(IPythonScriptAction)
    label = _(u"Add PythonScript Action")
    description = _(u"A PythonScript action can do almost anything.")
    form_name = _(u"Configure element")

    def create(self, data):
        a = PythonScriptAction()
        form.applyChanges(a, self.form_fields, data)
        return a


class PythonScriptEditForm(EditForm):
    """
    An edit form for the mail action
    """
    form_fields = form.FormFields(IPythonScriptAction)
    label = _(u"Edit PythonScript Action")
    description = _(u"A PythonScript action can do almost anything.")
    form_name = _(u"Configure element")
