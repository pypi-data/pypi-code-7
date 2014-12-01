from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from Products.CMFCore.utils import getToolByName
from uwosh.transitionbuttons.interfaces import IButtonSettings

from AccessControl.PermissionRole import rolesForPermissionOn

from zope.component import queryUtility
from plone.registry.interfaces import IRegistry
from string import split
import json

class ButtonViewlet(ViewletBase):
    render = ViewPageTemplateFile('js_viewlet.pt')
    defaultWorkflow = False
    settings = []

    def isPanelDisabled(self):

        memTool = getToolByName(self, 'portal_membership')
        user = memTool.getAuthenticatedMember()
        res = user.getProperty('buttonsDisabled')

        if( res == False or res == True ):
            return res
        else:
            #If for some reason, the value isn't set, assume it's disabled.
            # "True" means "Yes, it IS disabled"
            return True

    def isPageTypeAllowed(self):
        # If the current content type isn't enabled, stop here
        settings = self.getSettings()
        types = settings.EnabledTypes
        if types:
            if self.context.portal_type not in types:
                return False
            else:
                return True
        else:
            #This implies that there are no enabled types
            #Somewhat counterintuitively, we assume that this means
            #everything is allowed
            return True

    def isPanelAllowed(self):
        if self.isPageTypeAllowed() and not self.isPanelDisabled():
            return True

        return False

    # gets the settings from the add-on control panel
    def getSettings(self):
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IButtonSettings, False)
        return settings

    def getDefaultWorkflow(self):

        if self.defaultWorkflow != False:
            return self.defaultWorkflow

        wfType = self.context.portal_type
        chains = self.context.portal_workflow._chains_by_type
        
        wf_tool = getToolByName(self, 'portal_workflow')

        if wfType in chains:
            defaultWorkflow = chains[wfType]
            if len(defaultWorkflow) == 0:
                defaultWorkflow = wf_tool.getChainForPortalType(self.context.portal_type)   
        else:
            defaultWorkflow = wf_tool.getChainForPortalType(self.context.portal_type)

        try:
            defaultWorkflow = defaultWorkflow[0]
        except IndexError:
            #This means that the default wf is 
            #non-existent. This is a weird, but valid possibility.
            defaultWorkflow = False

        self.defaultWorkflow = defaultWorkflow

        return defaultWorkflow

    def getWFState(self):
        wf_tool = getToolByName(self, 'portal_workflow')

        try:
            state = wf_tool.getInfoFor(self.context, 'review_state')
            return state
        except:
            return False

    def getStateDescription(self):

        wf_tool = getToolByName(self, 'portal_workflow')
        defaultWorkflow = self.getDefaultWorkflow()

        state = self.getWFState()

        if not wf_tool:
            return False

        if not defaultWorkflow:
            return False

        try:
            desc = wf_tool[ defaultWorkflow ].states[state].description
        except:
            return False

        return desc

    def getTransitions(self):

        defaultWorkflow = self.getDefaultWorkflow()

        wf_tool = getToolByName(self, 'portal_workflow')

        transitions = wf_tool[ defaultWorkflow ].transitions
        transitionList = [];

        if transitions:
            for transition in transitions:
                transitionList.append(transition)

            return transitionList
        else:
            return False

    def getSite(self):
        return self.context.portal_url()

    def getPreferencesUrl(self):
        base = self.getSite()
        base += '/@@personal-preferences'

        return base

    def setJson(self):

        panelSettings = self.getSettings()
        wf = self.getDefaultWorkflow()

        settings = {}
        if self.isPanelAllowed() and wf != False:
            settings["allowedTransitions"] = self.getTransitions()
            settings["wfState"] = self.getWFState() 
            settings["stateDescription"] = self.getStateDescription()
            settings["pageElement"] = panelSettings.pageElement
            settings["floating"] = panelSettings.floating
            settings["preferencesUrl"] = self.getPreferencesUrl()
            settings["floatLocation"] = panelSettings.floatLocation
            settings["floatSpacing"] = panelSettings.floatSpacing

        return json.dumps(settings, sort_keys=False)

    def update(self):

        self.buttonJson = self.setJson()

