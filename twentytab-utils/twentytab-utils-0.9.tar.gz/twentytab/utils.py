"""
Contains many common functions
"""
import time


def datetimeToUnix(date):
    """
    Transform a datetime in unix format with milliseconds
    """
    return int(time.mktime(date.timetuple()) * 1000)


def datetimeToUnixSec(date):
    """
    Transform a datetime in unix format
    """
    return int(time.mktime(date.timetuple()))


def compare_dicts(dict1, dict2):
    """
    Checks if dict1 equals dict2
    """
    for k, v in dict2.items():
        if v != dict1[k]:
            return False
    return True


def getItalianAccentedVocal(vocal, acc_type="g"):
    """
    It returns given vocal with grave or acute accent 
    """
    vocals = {'a': {'g': u'\xe0', 'a': u'\xe1'},
              'e': {'g': u'\xe8', 'a': u'\xe9'},
              'i': {'g': u'\xec', 'a': u'\xed'},
              'o': {'g': u'\xf2', 'a': u'\xf3'},
              'u': {'g': u'\xf9', 'a': u'\xfa'}}
    return vocals[vocal][acc_type]


def _av(vocal, acc_type="g"):
    """
    It's a shortcut to getAccentedVocal function
    """
    return getItalianAccentedVocal(vocal, acc_type)
