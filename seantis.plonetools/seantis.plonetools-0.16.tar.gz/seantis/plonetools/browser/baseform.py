from five import grok

from z3c.form import button
from z3c.form.interfaces import ActionExecutionError
from plone.z3cform.fieldsets.extensible import ExtensibleForm

from zope.interface import Invalid

from plone.directives.form import Form

from seantis.plonetools import _
from seantis.plonetools.browser.shared import (
    TranslateMixin,
    StatusMessageMixin
)


class BaseForm(ExtensibleForm, Form, TranslateMixin, StatusMessageMixin):
    """ Baseform which should serve as a base for any and all Plone Forms
    by Seantis. It abstracts away some complexity from the underlying z3c forms
    and provides often used methods.

    The goal of this class is to remove duplicated code throughout our
    projects.

    Note, to use fieldsets/widget hints and so forth you need to have a schema
    inheriting from plone.supermodel.model.Schema:

    class ISchema(plone.supermodel.model.Schema)
        pass

    And a form like this:

    class Form(BaseForm, plone.autoform.form.AutoExtensibleForm):

        schema = IMySchema

    """

    grok.baseclass()

    created_msg = _(u"Item created")
    changed_msg = _(u"Changes saved")
    unchanged_msg = _(u"No changes saved")

    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)

        try:
            from plone.directives.dexterity import AddForm
            self.is_add_form = isinstance(self, AddForm)
        except ImportError:
            self.is_add_form = False

    def update(self):
        self.prepare_actions()
        super(BaseForm, self).update()

    def updateActions(self):
        super(BaseForm, self).updateActions()

        # add the css class to the buttons which have a custom css class
        for action in self.available_actions:
            if 'css_class' in action:
                self.actions[action['name']].addClass(action['css_class'])

    @property
    def available_actions(self):
        """ Returns the available actions (buttons) of this form. The default
        style of doing this by using decorators has the disadvantage that
        buttons may not be inherited.

        For example, we always redefine 'Cancel' for all forms.

        By overriding this form and returning a list of dictionaries, the
        buttons can easily be defined. For example:

        return [
            dict(name='delete', title=_(u'Delete'), css_class='destructive'),
            dict(name='cancel', title=_(u'Cancel'))
        ]

        The handlers for these actions are handle_delete and handle_cancel.
        As should be obvious, the function is implicitly defined as
        handle_<action-name>.

        All actions always go through handle_action first, bevore the
        respective functions are called.

        handle_save and handle_cancel are available as default handlers.

        """

        yield dict(name='save', title=_(u'Save'), css_class='context')
        yield dict(name='cancel', title=_(u'Cancel'))

    @property
    def success_url(self):
        """ Redirect used when handle_save runs successfully. """
        return self.context.absolute_url()

    @property
    def cancel_url(self):
        """ Redirect used when the user clicks on handle_cancel. """
        return self.context.absolute_url()

    def prepare_actions(self):
        """ Takes the actions defined in available_actions and adds
        them as buttons and handlers. Note that the css_class is added
        using updateActions.

        """
        self.buttons = button.Buttons()
        self.handlers = button.Handlers()

        for action in self.available_actions:

            btn = button.Button(title=action['title'], name=action['name'])
            self.buttons += button.Buttons(btn)

            button_handler = button.Handler(btn, self.__class__.handle_action)
            self.handlers.addHandler(btn, button_handler)

    def handle_action(self, action):
        """ All actions flow through this handler by default. It checks
        for the availability of handle_<action_name> and calls them
        if they are present.

        """
        button_handler_id = 'handle_{name}'.format(name=action.__name__)
        button_handler_fn = getattr(self.__class__, button_handler_id)

        assert button_handler_fn, """Button {name} expects a button handler
        funnction named 'handle_{name}', this handler could not be found
        on class {cls}.""".format(name=action.__name__, cls=self.__class__)

        return button_handler_fn(self)

    def before_save(self, data):
        """ Called with the validated data before the changes are applied.
        Liast chance to add custom validations.

        """
        pass

    def handle_save(self):
        """ Default handler for saves. Gets the data, applies them and
        shows a message if there were changes. Redirects to self.success_url
        if no validation errors stopped the process.

        """
        data = self.parameters

        if data is None:
            return

        self.before_save(data)

        if self.is_add_form:
            obj = self.createAndAdd(data)
            if obj is not None:
                self._finishedAdd = True
                self.message(self.created_msg)
            else:
                return
        else:
            if self.applyChanges(data):
                self.message(self.changed_msg)
            else:
                self.message(self.unchanged_msg)

        self.request.response.redirect(self.success_url)

    def handle_cancel(self):
        self.request.response.redirect(self.cancel_url)

    @property
    def parameters(self):
        """ Extracts the form data and returns a dictionary or None if
        something went wrong. If something does go wrong, the error message
        is automatically set.

        """
        data, errors = self.extractData()

        if errors:
            self.status = self.formErrorsMessage
            return None
        else:
            return data

    def raise_action_error(self, msg):
        """ Raise the given message as action execution error, which will
        pop up on top of the form.

        """
        raise ActionExecutionError(Invalid(msg))
