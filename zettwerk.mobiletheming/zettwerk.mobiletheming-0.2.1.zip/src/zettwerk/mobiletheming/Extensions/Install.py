from Products.CMFCore.utils import getToolByName


def uninstall(portal):
    ## run default uninstall profile
    setup_tool = getToolByName(portal, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile(
        'profile-zettwerk.mobiletheming:uninstall'
    )

    ## manual cleanup: remove the link to the mobilesettings view
    cp_tool = getToolByName(portal, 'portal_controlpanel')
    cp_tool.unregisterConfiglet('mobilesettings')

    ## unregister the local ITransform adapter
    sm = portal.getSiteManager()
    for adapter in sm.registeredAdapters():
        if adapter.name == 'zettwerk_mobiletheming_transform':
            sm.unregisterAdapter(
                adapter.factory,
                adapter.required,
                adapter.provided,
                adapter.name)
            del adapter
            break

    return "Ran all uninstall steps."
