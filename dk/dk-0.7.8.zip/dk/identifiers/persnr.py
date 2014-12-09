# -*- coding: utf-8 -*-

"""Norwegian 'Personnummer' module.

"""

import datetime


class PersnrException(ValueError):
    "Base exception for persnr module."
    pass


def multiply_reduce(avec, bvec):
    """Multiply each item in a with corresponding item in b,
       then sum the result.
    """
    return sum((aval * bval) for (aval, bval) in zip(avec, bvec))


def is_persnr(pnr):
    "Return True if ``pnr`` is a valid persnr."
    try:
        return check_pnr_structure(pnr)

    except PersnrException:
        return False

    except ValueError:
        return False


def splitpnr(pnr):
    "Split the personnummer into it's parts."
    if len(pnr) != 11:
        raise PersnrException(
            "Persnr: incorrect length (%s): %s" % (len(pnr), pnr))
    res = {
        'day': pnr[:2],
        'month': pnr[2:4],
        'year': pnr[4:6],
        'individ': pnr[6:9],
        'gender': 'F' if (int(pnr[8]) % 2 == 0) else 'M',
        'k1': pnr[9:10],
        'k2': pnr[10:11],
        'dnr': False,
    }
    if pnr[0] >= '4':
        res['dnr'] = True
        res['day'] = str(int(res['day']) - 40)
        
    return res


def calc_year(yr2, inr):
    "Find the 4-digit year, following all the rules."
    if 900 <= inr <= 999:
        if yr2 >= 40:
            return 1900 + yr2
        else:
            return 2000 + yr2

    if 500 <= inr <= 999:
        if yr2 <= 39:
            return 2000 + yr2

    if 500 <= inr <= 749:
        if yr2 >= 55:
            return 1800 + yr2

    if 0 <= inr <= 499:
        return 1900 + yr2

    raise PersnrException('Persnr: individ nr mismatch')


def year(pnr):
    "Extract the year from pnr."
    pdata = splitpnr(pnr)
    inr = int(pdata['individ'])
    yr2 = int(pdata['year'])
    return calc_year(yr2, inr)


def date(pnr):
    "Find the birth date and return as datetime.date() object."
    pdata = splitpnr(pnr)
    day = int(pdata['day'])
    month = int(pdata['month'])
    yr4 = year(pnr)
    return datetime.date(yr4, month, day)


def gender(pnr):
    "Extract the gender as 'M' for male and 'F' for female."
    return splitpnr(pnr)['gender']


def check_individnr(inr, year4):
    "Hopelessly inefficient way of checking the individnr."
    # http://no.wikipedia.org/wiki/Personnummer
    #  000-499:  1900-1999
    #  500-749:  1855-1899
    #  500-999:  2000-2039
    #  900-999:  1940-1999
    yrange = set()
    if 0 <= inr < 500:
        yrange |= set(range(1900, 2000))
    if 500 <= inr < 750:
        yrange |= set(range(1855, 1900))
    if 500 <= inr < 1000:
        yrange |= set(range(2000, 2039))
    if 900 <= inr < 1000:
        yrange |= set(range(1940, 2000))
    if year4 not in set(yrange):
        raise PersnrException('Persnr: individ nr mismatch')

    return True


def check_pnr_structure(pnr):
    "Raise exception if the structure of the personnummer is incorrect."
    splitpnr(pnr)       # throws on error
    date(pnr)           # throws on error
    check_parity(pnr)   # throws on error
    return True


def check_pnr(pnr, birthday, sex):
    """
       >>> check_pnr('02057035768', datetime.date(1970, 5, 2), 'm')
       True
    """
    # check that the date is valid (birthday argument is valid
    # by construction).
    data = splitpnr(pnr)
    
    day = int(data['day'])
    if day != birthday.day:
        raise PersnrException('Persnr: Invalid Date')
    month = int(data['month'])
    if month != birthday.month:
        raise PersnrException('Persnr: Invalid Date')
    yr2 = int(data['year'])  # the two digit year
    if yr2 != birthday.year % 100:
        raise PersnrException('Persnr: Invalid Date')

    individnr = int(data['individ'])
    check_individnr(individnr, birthday.year)

    # males have an odd digit in position 8, females an even digit.
    if sex not in 'mMfF':
        raise PersnrException("Persnr: unknown gender (%r)" % sex)
    
    if sex.upper() != data['gender']:
        raise PersnrException({
            'M': 'Persnr: even male',
            'F': 'Persnr: odd female'
        }.get(sex, 'Persnr: unknown gender (%r)' % sex))
    
    return check_parity(pnr)


VEKT1 = [3, 7, 6, 1, 8, 9, 4, 5, 2, 1, 0]
VEKT2 = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2, 1]


def check_parity(pnr):
    "Check the last two digits, which are parity controls."
    pnr = [int(v) for v in pnr]

    if multiply_reduce(pnr, VEKT1) % 11 != 0:
        raise PersnrException('Dette er ikke et gyldig fødselsnr. [ktrl-1]')
    if multiply_reduce(pnr, VEKT2) % 11 != 0:
        raise PersnrException('Dette er ikke et gyldig fødselsnr. [ktrl-2]')

    return True


def calc_par1(ppnr):
    "Calculate the first parity digit."
    for i in range(1, 10):
        tmp = [int(v) for v in ppnr[:9]] + [i]
        val = multiply_reduce(tmp, VEKT1)
        if val % 11 == 0:
            return i
    raise PersnrException(ppnr)


def calc_par2(ppnr):
    "Calculate the second parity digit."
    for i in range(1, 10):
        tmp = [int(v) for v in ppnr[:10]] + [i]
        val = multiply_reduce(tmp, VEKT2)
        if val % 11 == 0:
            return i
    raise PersnrException(ppnr)


def calc_parity(ppnr):
    "Calculate parity digits."
    tmp = ppnr + str(calc_par1(ppnr))
    val = tmp + str(calc_par2(tmp))
    return val


def generate_pnr(day, gndr):
    "Generate all persnrs for a given gender on a given day."
    datepart = day.strftime('%d%m%y')
    if gndr == 'M':
        inrs = range(1, 1000, 2)
    else:
        inrs = range(0, 1000, 2)

    for inr in inrs:
        try:
            yield calc_parity('%s%03d' % (datepart, inr))
        except PersnrException:
            pass


def list_pnr(day=None, gender='M'):  # pylint: disable=W0621
    "List all persnrs for a given gender on a given day."
    if day is None:
        day = datetime.date.today()
    return list(generate_pnr(day, gender))


def testing_persnr(n=0):
    """Create a persnr for use in unit tests.
       If different tests need separate persnr, pass a unique small integer as
       a parameter.
    """
    return list_pnr(datetime.date(2050, 1, 1))[n]


if __name__ == "__main__":
    # invoke with python -m core.persnr
    for _pnr in list_pnr():
        print _pnr
