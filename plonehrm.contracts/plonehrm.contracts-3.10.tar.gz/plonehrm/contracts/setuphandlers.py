from Products.CMFCore.utils import getToolByName


def setup(context):
    # This is the main method that gets called by genericsetup.
    if context.readDataFile('plonehrm.contracts.txt') is None:
        return
    site = context.getSite()
    logger = context.getLogger('plonehrm')
    add_currency_property(site, logger)


def add_currency_property(site, logger):
    """Add a currency property to portal_properties.plonehrm_properties.

    We do that in python code instead of in propertiestool.xml to
    avoid overwriting changes by the user.

    Plus: there was a problem importing a string property with
    '&euro;' as value:

    ExpatError: /test/portal_properties: undefined entity: line 7, column 42
    """
    portal_props = getToolByName(site, 'portal_properties')
    props = portal_props.plonehrm_properties
    propname = 'currency'
    if not props.hasProperty(propname):
        value = '&euro;'
        props._setProperty(propname, value, 'string')
        logger.info('Added property %r with default value %r',
                    propname, value)
