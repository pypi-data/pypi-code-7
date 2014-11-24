# =============================================================================
# Copyright [2014] [Kevin Carter]
# License Information :
# This software has no warranty, it is provided 'as is'. It is your
# responsibility to validate the behavior of the routines and its accuracy
# using the code provided. Consult the GNU General Public license for further
# details (see GNU General Public License).
# http://www.gnu.org/licenses/gpl.html
# =============================================================================


def is_int(value):
    """Return value as int if the value can be an int.

    :param value: ``str``
    :return: ``int`` || ``str``
    """
    try:
        return int(value)
    except ValueError:
        return value


def ensure_string(obj):
    """Return String and if Unicode convert to string.

    :param obj: ``str`` || ``unicode``
    :return: ``str``
    """
    if isinstance(obj, unicode):
        return str(obj.encode('utf8'))
    else:
        return obj


def dict_update(base_dict, update_dict):
    """Return an updated dictionary.

    If ``update_dict`` is a dictionary it will be used to update the `
    `base_dict`` which is then returned.

    :param request_kwargs: ``dict``
    :param kwargs: ``dict``
    :return: ``dict``
    """
    if isinstance(update_dict, dict):
        base_dict.update(update_dict)

    return base_dict
