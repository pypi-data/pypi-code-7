from Products.validation.interfaces import ivalidator
from Products.validation import validation
from Products.validation.validators.RegexValidator import RegexValidator
from Products.plonehrm import PloneHrmMessageFactory as _
from zope.i18n import translate


class MaxDaysPerWeek:
    __implements__ = (ivalidator,)

    def __init__(self, name):
        self.name = name

    def __call__(self, value, *args, **kwargs):
        value = float(value)
        maxdays = 7
        if value < 0 or value > maxdays:
            error = _("Please enter 0 to 7 days.")
            return translate(error)
        return value

# Allow both commas and dots as decimal points.  And do not allow
# exponentials (like 5.0e2).

isCurrency = RegexValidator(
    'isCurrency',
    r'^([+-]?)(?=\d|[,\.]\d)\d*([,\.]\d*)?$',
    title='', description='',
    errmsg='is not a decimal number.')

validation.register(isCurrency)
