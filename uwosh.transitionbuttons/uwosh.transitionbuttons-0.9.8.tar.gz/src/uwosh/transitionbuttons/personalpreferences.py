from plone.app.users.browser.personalpreferences import PersonalPreferencesPanel
from plone.app.users.browser.personalpreferences import LanguageWidget
from plone.app.users.browser.personalpreferences import WysiwygEditorWidget
from zope.formlib import form
from uwosh.transitionbuttons.userdataschema import IEnhancedUserDataSchema

class CustomPersonalPreferencesPanel(PersonalPreferencesPanel):

    form_fields = form.FormFields(IEnhancedUserDataSchema)
    # Apply same widget overrides as in the base class
    form_fields['language'].custom_widget = LanguageWidget
    form_fields['wysiwyg_editor'].custom_widget = WysiwygEditorWidget
