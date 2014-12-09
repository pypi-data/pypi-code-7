# -*- coding: utf-8 -*-

u"""Strukturen på våre kid-nummer:
    sensornr = '0123' # fire siffer
    kandidatnr = '01234' # fem siffer

    kiddata = sensornr + kandidatnr
    kid = kiddata + kontroll_10(kiddata)
"""

# pylint:disable=W0141


def generate_kids(sensornr, count, start=0):
    """Generate ``count`` kid numbers for sensor with ``sensornr`` (prefix),
       starting at ``start`` (for the counting part of the kid).
    """
    while count > 0:
        data = str(sensornr) + ('%05d' % start)
        start += 1
        yield (data + kontroll_10(data))
        count -= 1


def create_kids(tctr, sequencenum):
    "BFP-8"
    tctrtype, tctrnum = tctr.split('-', 1)
    res = '1' if tctrtype.lower() == 'nt' else '2'
    res += '%04d' % int(tctrnum)
    res += '%08d' % sequencenum
    c1 = kontroll_10(res)
    res = res[:7] + c1 + res[7:]
    res += kontroll_10(res)
    return res


def is_valid_kid(s):
    """Test if s is a valid kid number.
    """
    if s is None:
        return True
    if type(s) not in (str, unicode):
        return False
    if len(s) != 10:
        return False
    try:
        n = int(s)
        data, kontroll = divmod(n, 10)
        return kontroll_10(str(data)) == str(kontroll)
    except:
        return False
    return True


def vekt(n, base):
    """Funksjon som gir en repeterende serie med siffer fra ``base``, som
       har lengde ``n``.

       For kontroll_10 er vekttall-serien: 2,1,2,1,2,1...
       for kontroll_11 er vekttall-serien: 2,3,4,5,6,7,2,3,4,5,...
    """
    for i in range(n):
        yield base[i % len(base)]

        
def kontroll_10(s):
    u"""MOD10 algoritmen.

       MOD10 er forkortelse for Modulus 10 algoritmen, også kalt
       Luhn-algoritmen etter oppfinneren Hans Peter Luhn. Modulus 10
       algoritmen benyttes bl.a. som beregningsmetode for et
       kontrollsiffer i KID-numre på bankenes innbetalingsblanketter.
       (http://no.wikipedia.org/wiki/MOD10)
    """
    siffer = map(int, list(s))[::-1]  # reversed
    vekttall = vekt(len(siffer), [2, 1])
    produkter = ''.join(str(s * v) for (s, v) in zip(siffer, vekttall))
    siffersum = sum(int(c) for c in produkter)
    entallsiffer = siffersum % 10
    if entallsiffer == 0:
        kontrollsiffer = entallsiffer
    else:
        kontrollsiffer = 10 - entallsiffer
    return str(kontrollsiffer)


def kontroll_11(s):
    u"""MOD11 algoritmen.

        MOD11 er forkortelse for Modulus11. Modulus11 benyttes blant
        annet som beregningsmetode for et kontrollsiffer i kontonumre
        i norske banker, organisasjonsnummer og for det siste sifferet
        i norske fødselsnummer. (Norske fødselsnummer har to
        kontrollsifre, det nest siste er også et modulo 11
        kontrollsiffer, men ved beregningen av dette benyttes det
        multiplikatorer i en annen og uregelmessig rekkefølge).
        (http://no.wikipedia.org/wiki/MOD11)
    """
    # vi bruker ikke denne algoritmen
    siffer = map(int, list(s))[::-1]  # reversed
    vekttall = vekt(len(siffer), range(2, 8))
    psum = sum(s * v for (s, v) in zip(siffer, vekttall))
    rest = psum % 11
    if rest == 0:
        kontrollsiffer = '0'
    elif rest == 1:
        kontrollsiffer = '-'
    else:
        kontrollsiffer = str(11 - rest)
    return kontrollsiffer
