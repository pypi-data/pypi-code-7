import pytz
from suds import sudsobject
from datetime import datetime
from dateutil.parser import parse as dateutil_parser

# Specific signature keys excludes for API types
SIGNATURE_EXCLUDES = {
    'createPaiementIdentInfo': [
        'cvv'
    ],
    'customerModifyInfo': [
        'customerStatus',
        'customerAddressNumber',
        'customerDistrict'
    ],
    'identCreationInfo': [
        'customerStatus',
        'customerAddressNumber',
        'customerDistrict',
        'customerFirstName',
        'customerLegalName'
    ]
}

# Keys to use for response signature calculation
RESPONSE_SIGNATURE_KEYS = [
    'timestamp',
    'errorCode',
    'extendedErrorCode',
    'identId',
    'transactionId',
    'subscriptionId',
    'transactionStatus',
    'paymentWarranty',
    'amount',
    'authNumber',
    'authorizationDate'
]


def get_factory_data(factory, keys=None, excludes=None):
    """
    Returns the factory data as list of tuples

    :param keys: Explicit list of keys to use for signature calculation. If None,
    uses all the fields from the Factory.
    :type keys: list
    :param excludes: A list of fields to exclude for signature calculation
    :type excludes: list
    :returns: A list of tuples as (key, value)
    :rtype: list
    """
    values = []
    keys = keys or factory.__keylist__
    excludes = set(excludes or [])

    # Append default excludes
    excludes.update(
        SIGNATURE_EXCLUDES.get(factory.__metadata__.sxtype.name, []))
    excludes.add('extInfo')

    for k in keys:

        # If key is an excludes one, continue
        if k in excludes:
            continue

        v = getattr(factory, k, None)

        # If value is a suds Object, return its data
        if isinstance(v, sudsobject.Object):
            object_values = get_factory_data(v)

            # Only serialize objects with defined values
            if any(list(zip(*object_values))[1]):
                values.extend(object_values)
            else:
                values.append((k, ''))

        else:
            values.append((k, v))

    return values


def get_formatted_value(value):
    """
    Returns the formatted value for the signature calculation
    Uses rules specified in Systempay documentation :

        - bool is interpreted as an integer (O or 1)
        - empty values (except integers) are considered as an empty string
        - datetime values are formatted like 'YYYMMDD' using UTC timezone

    :param value: The input value to format
    :type value: any
    :returns: The formatted value
    :rtype: str
    """
    # Boolean format
    if isinstance(value, bool):
        return str(int(value))

    # Integer value
    if isinstance(value, int):
        return str(value)

    # Empty value
    if not value:
        return ''

    # Datetime format
    if isinstance(value, datetime):
        return value.strftime('%Y%m%d')

    # String datetime format
    try:
        d = dateutil_parser(value).astimezone(pytz.UTC)
        return d.strftime('%Y%m%d')
    except:
        pass

    return value
