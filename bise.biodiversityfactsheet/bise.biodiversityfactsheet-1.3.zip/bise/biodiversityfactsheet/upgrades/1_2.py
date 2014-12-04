from Products.CMFCore.utils import getToolByName

PROFILE_ID = 'profile-bise.biodiversityfactsheet:default'


def upgrade(context, logger=None):
    if logger is None:
        from logging import getLogger
        logger = getLogger('bise.biodiversityfactsheet.upgrades.1_2')

    upgrade_diff_tool(context, logger)
    logger.info('Upgraded Diff Tool')


def upgrade_diff_tool(context, logger):
    # Re-run profile installation
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'typeinfo')