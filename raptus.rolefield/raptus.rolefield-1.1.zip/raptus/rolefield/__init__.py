from zope.i18nmessageid import MessageFactory
_ = MessageFactory('raptus.rolefield')

try: 
    from Products.PlacelessTranslationService.utility import PTSTranslationDomain
    raptusrolefielddomain = PTSTranslationDomain('raptus.rolefield')
except ImportError: # Plone 4 
    pass