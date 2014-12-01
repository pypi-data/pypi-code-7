from plone.app.registry.browser import controlpanel

from uwosh.transitionbuttons.interfaces import IButtonSettings, _


class ButtonSettingsEditForm(controlpanel.RegistryEditForm):

    schema = IButtonSettings
    label = _(u"Transition Buttons")
    description = _(u"""""")

    def updateFields(self):
        super(ButtonSettingsEditForm, self).updateFields()


    def updateWidgets(self):
        super(ButtonSettingsEditForm, self).updateWidgets()

class ButtonSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = ButtonSettingsEditForm