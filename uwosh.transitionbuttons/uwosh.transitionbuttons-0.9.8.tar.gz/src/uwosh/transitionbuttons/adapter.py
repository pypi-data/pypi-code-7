from plone.app.users.browser.personalpreferences import PersonalPreferencesPanelAdapter
from uwosh.transitionbuttons.userdataschema import IEnhancedUserDataSchema
from zope.interface import implements
from uwosh.transitionbuttons.interfaces import IButtonConfigLayer

class EnhancedUserDataPanelAdapter(PersonalPreferencesPanelAdapter):
    """
    """
    implements(IEnhancedUserDataSchema)

    def get_buttonDisabled(self):
        return self.context.getProperty('buttonsDisabled', '')
    def set_buttonsDisabled(self, value):
        return self.context.setMemberProperties({'buttonsDisabled': value})
    buttonsDisabled = property(get_buttonDisabled, set_buttonsDisabled)
