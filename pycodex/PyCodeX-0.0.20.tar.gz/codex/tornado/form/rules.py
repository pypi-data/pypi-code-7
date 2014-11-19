from wtforms import validators

# _error_messages = {
#     'required' : "The %s field is required.",
#     'isset' : "The %s field must have a value.",
#     'valid_email' : "The %s field must contain a valid email address.",
#     'valid_emails' : "The %s field must contain all valid email addresses.",
#     'valid_url' : "The %s field must contain a valid URL.",
#     'valid_ip' : "The %s field must contain a valid IP.",
#     'exact_length'       : "The %s field must be exactly %s characters in length.",
#     'alpha'              : "The %s field may only contain alphabetical characters.",
#     'alpha_numeric'      : "The %s field may only contain alpha-numeric characters.",
#     'alpha_dash'         : "The %s field may only contain alpha-numeric characters, underscores, and dashes.",
#     'numeric'            : "The %s field must contain only numbers.",
#     'is_numeric'         : "The %s field must contain only numeric characters.",
#     'integer'            : "The %s field must contain an integer.",
#     'regex_match'        : "The %s field is not in the correct format.",
#     'is_unique'          : "The %s field must contain a unique value.",
#     'is_natural'         : "The %s field must contain only positive numbers.",
#     'is_natural_no_zero' : "The %s field must contain a number greater than zero.",
#     'decimal'            : "The %s field must contain a decimal number.",
#     'less_than'          : "The %s field must contain a number less than %s.",
#     'greater_than'       : "The %s field must contain a number greater than %s.",
# }

class EqualTo(validators.EqualTo):
    """
    Compares the values of two fields.

    :param fieldname:
        The name of the other field to compare to.
    :param message:
        Error message to raise in case of a validation error. Can be
        interpolated with `%(other_label)s` and `%(other_name)s` to provide a
        more helpful error.
    """
    def __init__(self, fieldname, message=None):
        if message is None:
            message = "{{field_label}} field does not match the %(other_label)s field."
        super().__init__(fieldname, message)

class Length(validators.Length):
    """
    Validates the length of a string.

    :param min:
        The minimum required length of the string. If not provided, minimum
        length will not be checked.
    :param max:
        The maximum length of the string. If not provided, maximum length
        will not be checked.
    :param message:
        Error message to raise in case of a validation error. Can be
        interpolated using `%(min)d` and `%(max)d` if desired. Useful defaults
        are provided depending on the existence of min and max.
    """
    def __init__(self, min=-1, max=-1, message=None):
        if message is None:
            if min > -1 and max <= -1:
                message = "{{field_label}} field must be at least %(min)d characters in length."
            elif min <= -1 and max > -1:
                message = "{{field_label}} field can not exceed %(max)d characters in length."
            elif min > -1 and max > -1:
                message = "{{field_label}} field must be between %(min)d and %(max)d characters long."
        super().__init__(min, max, message)

class NumberRange(validators.NumberRange):
    """
    Validates that a number is of a minimum and/or maximum value, inclusive.
    This will work with any comparable number type, such as floats and
    decimals, not just integers.

    :param min:
        The minimum required value of the number. If not provided, minimum
        value will not be checked.
    :param max:
        The maximum value of the number. If not provided, maximum value
        will not be checked.
    :param message:
        Error message to raise in case of a validation error. Can be
        interpolated using `%(min)s` and `%(max)s` if desired. Useful defaults
        are provided depending on the existence of min and max.
    """
    def __init__(self, min=None, max=None, message=None):
        if message is None:
            if max is None:
                message = "{{field_label}} field must contain a number at least %(min)s."
            elif min is None:
                message = "{{field_label}} field must contain a number at most %(max)s."
            else:
                message = "{{field_label}} field must contain a number between %(min)s and %(max)s."
        super().__init__(min, max, message)

class Optional(validators.Optional):
    """
    Allows empty input and stops the validation chain from continuing.

    If input is empty, also removes prior errors (such as processing errors)
    from the field.

    :param strip_whitespace:
        If True (the default) also stop the validation chain on input which
        consists of only whitespace.
    """
    def __init__(self, strip_whitespace=True):
        super().__init__(strip_whitespace)

class DataRequired(validators.DataRequired):
    """
    Validates that the field contains coerced data. This validator will stop
    the validation chain on error.

    If the data is empty, also removes prior errors (such as processing errors)
    from the field.

    **NOTE** this validator used to be called `Required` but the way it behaved
    (requiring coerced data, not input data) meant it functioned in a way
    which was not symmetric to the `Optional` validator and furthermore caused
    confusion with certain fields which coerced data to 'falsey' values like
    ``0``, ``Decimal(0)``, etc. Unless a very specific reason exists, we
    recommend using the :class:`InputRequired` instead.

    :param message:
        Error message to raise in case of a validation error.
    """
    def __init__(self, message=None):
        if message is None:
            message = "{{field_label}} field is required."
        super().__init__(message)

class Required(DataRequired):
    """
    Legacy alias for DataRequired.

    This is needed over simple aliasing for those who require that the
    class-name of required be 'Required.'

    This class will start throwing deprecation warnings in WTForms 1.1 and be removed by 1.2.
    """

class InputRequired(validators.InputRequired):
    """
    Validates that input was provided for this field.

    Note there is a distinction between this and DataRequired in that
    InputRequired looks that form-input data was provided, and DataRequired
    looks at the post-coercion data.
    """
    def __init__(self, message=None):
        if message is None:
            message = "{{field_label}} field is required."
        super().__init__(message)

class Regexp(validators.Regexp):
    """
    Validates the field against a user provided regexp.

    :param regex:
        The regular expression string to use. Can also be a compiled regular
        expression pattern.
    :param flags:
        The regexp flags to use, for example re.IGNORECASE. Ignored if
        `regex` is not a string.
    :param message:
        Error message to raise in case of a validation error.
    """
    def __init__(self, regex, flags=0, message=None):
        if message is None:
            message = "{{field_label}} field is not in the correct format."
        super().__init__(regex, flags, message)

class Alpha(Regexp):
    def __init__(self, message=None):
        if message is None:
            message = "{{field_label}} field may only contain alphabetical characters."
        super().__init__('^[a-zA-Z]+$', message=message)

class AlphaDash(Regexp):
    def __init__(self, message=None):
        if message is None:
            message = "{{field_label}} field may only contain alphabetical characters, underscores, and dashes."
        super().__init__('^[a-zA-Z_-]+$', message=message)

class AlphaSpace(Regexp):
    def __init__(self, message=None):
        if message is None:
            message = "{{field_label}} field may only contain alphabetical characters and spaces."
        super().__init__('^[a-zA-Z ]+$', message=message)

class AlphaSpaceDash(Regexp):
    def __init__(self, message=None):
        if message is None:
            message = "{{field_label}} field may only contain alphabetical characters, underscores, dashes and spaces."
        super().__init__('^[a-zA-Z_- ]+$', message=message)

class AlphaNumeric(Regexp):
    def __init__(self, message=None):
        if message is None:
            message = "{{field_label}} field may only contain alpha-numeric characters."
        super().__init__('^[a-zA-Z0-9]+$', message=message)

class AlphaNumericDash(Regexp):
    def __init__(self, message=None):
        if message is None:
            message = "{{field_label}} field may only contain alpha-numeric characters, underscores, and dashes."
        super().__init__('^[a-zA-Z0-9_-]+$', message=message)

class AlphaNumericSpace(Regexp):
    def __init__(self, message=None):
        if message is None:
            message = "{{field_label}} field may only contain alpha-numeric characters and spaces."
        super().__init__('^[a-zA-Z0-9 ]+$', message=message)

class AlphaNumericSpaceDash(Regexp):
    def __init__(self, message=None):
        if message is None:
            message = "{{field_label}} field may only contain alpha-numeric characters, underscores, dashes and spaces."
        super().__init__('^[a-zA-Z0-9_- ]+$', message=message)

class Email(validators.Email):
    """
    Validates an email address. Note that this uses a very primitive regular
    expression and should only be used in instances where you later verify by
    other means, such as email activation or lookups.

    :param message:
        Error message to raise in case of a validation error.
    """
    def __init__(self, message=None):
        if message is None:
            message = "{{field_label}} field must contain a valid email address."
        super().__init__(message)

class IPAddress(validators.IPAddress):
    """
    Validates an IP address.

    :param ipv4:
        If True, accept IPv4 addresses as valid (default True)
    :param ipv6:
        If True, accept IPv6 addresses as valid (default False)
    :param message:
        Error message to raise in case of a validation error.
    """
    def __init__(self, ipv4=True, ipv6=False, message=None):
        if message is None:
            message = "{{field_label}} field must contain a valid IP."
        super().__init__(ipv4, ipv6, message)

class MacAddress(validators.MacAddress):
    """
    Validates a MAC address.

    :param message:
        Error message to raise in case of a validation error.
    """
    def __init__(self, message=None):
        if message is None:
            message = "{{field_label}} field must contain a valid MAC address."
        super().__init__(message)

class URL(validators.URL):
    """
    Simple regexp based url validation. Much like the email validator, you
    probably want to validate the url later by other means if the url must
    resolve.

    :param require_tld:
        If true, then the domain-name portion of the URL must contain a .tld
        suffix.  Set this to false if you want to allow domains like
        `localhost`.
    :param message:
        Error message to raise in case of a validation error.
    """
    def __init__(self, require_tld=True, message=None):
        if message is None:
            message = "{{field_label}} field must contain a valid URL."
        super().__init__(require_tld, message)

class UUID(validators.UUID):
    """
    Validates a UUID.

    :param message:
        Error message to raise in case of a validation error.
    """
    def __init__(self, message=None):
        if message is None:
            message = "{{field_label}} field must contain a valid UUID."
        super().__init__(message)

class AnyOf(validators.AnyOf):
    """
    Compares the incoming data to a sequence of valid inputs.

    :param values:
        A sequence of valid inputs.
    :param message:
        Error message to raise in case of a validation error. `%(values)s`
        contains the list of values.
    :param values_formatter:
        Function used to format the list of values in the error message.
    """
    def __init__(self, values, message=None, values_formatter=None):
        if message is None:
            message = "{{field_label}} field must contain one of: %(values)s."
        super().__init__(values, message, values_formatter)

class NoneOf(validators.NoneOf):
    """
    Compares the incoming data to a sequence of invalid inputs.

    :param values:
        A sequence of invalid inputs.
    :param message:
        Error message to raise in case of a validation error. `%(values)s`
        contains the list of values.
    :param values_formatter:
        Function used to format the list of values in the error message.
    """
    def __init__(self, values, message=None, values_formatter=None):
        if message is None:
            message = "{{field_label}} field must not contain one of: %(values)s."
        super().__init__(values, message, values_formatter)

email = Email
equal_to = EqualTo
ip_address = IPAddress
mac_address = MacAddress
length = Length
number_range = NumberRange
optional = Optional
required = Required
input_required = InputRequired
data_required = DataRequired
regexp = Regexp
url = URL
any_of = AnyOf
none_of = NoneOf