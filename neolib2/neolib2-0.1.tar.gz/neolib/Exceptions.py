
# General
class ParseException(Exception):
    pass

# Item
class InvalidItemID(Exception):
    pass

# Registration
class MissingRequiredAttribute(Exception):
    pass

class AttributeNotFound(Exception):
    pass

class UsernameNotAvailable(Exception):
    pass

class InvalidPassword(Exception):
    pass

class InvalidDetails(Exception):
    pass

class InvalidEmail(Exception):
    pass

class NeopetNotAvailable(Exception):
    pass

class InvalidNeopet(Exception):
    pass

#Shop
class WizardBanned(Exception):
    pass

# User
class NeopetsOffline(Exception):
    pass
