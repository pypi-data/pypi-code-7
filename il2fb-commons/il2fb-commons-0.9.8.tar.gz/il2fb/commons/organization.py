# -*- coding: utf-8 -*-

import os
import six

if six.PY2:
    from io import open

from candv import (
    Values, VerboseConstant, VerboseValueConstant, with_constant_class,
)

from . import SupportedLanguages
from .utils import translations


_ = translations.ugettext_lazy


class Belligerents(Values):
    none = VerboseValueConstant(0, _("neutral"))
    red = VerboseValueConstant(1, _("allies"))
    blue = VerboseValueConstant(2, _("axis"))
    green = VerboseValueConstant(3, _("green"))
    gold = VerboseValueConstant(4, _("gold"))
    purple = VerboseValueConstant(5, _("purple"))
    aqua = VerboseValueConstant(6, _("aqua"))
    maroon = VerboseValueConstant(7, _("maroon"))
    navy = VerboseValueConstant(8, _("navy"))
    emerald = VerboseValueConstant(9, _("emerald"))
    olive = VerboseValueConstant(10, _("olive"))
    magenta = VerboseValueConstant(11, _("magenta"))
    teal = VerboseValueConstant(12, _("teal"))
    orange = VerboseValueConstant(13, _("orange"))
    turquoise = VerboseValueConstant(14, _("turquoise"))
    brown = VerboseValueConstant(15, _("brown"))
    salad = VerboseValueConstant(16, _("salad"))


class Country(VerboseConstant):

    def __init__(self, belligerent, verbose_name=None, help_text=None):
        super(Country, self).__init__(verbose_name=verbose_name,
                                      help_text=help_text)
        self.belligerent = belligerent

    def merge_into_group(self, group):
        super(Country, self).merge_into_group(group)
        group.belligerent = self.belligerent


class Countries(with_constant_class(Country), Values):
    au = Country(Belligerents.red, _("Australia"))
    fi = Country(Belligerents.blue, _("Finland"))
    fr = Country(Belligerents.red, _("France"))
    de = Country(Belligerents.blue, _("Germany"))
    hu = Country(Belligerents.blue, _("Hungary"))
    jp = Country(Belligerents.blue, _("Japan"))
    it = Country(Belligerents.blue, _("Italy"))
    nl = Country(Belligerents.red, _("Netherlands"))
    nz = Country(Belligerents.red, _("New Zealand"))
    pl = Country(Belligerents.red, _("Poland"))
    ro = Country(Belligerents.blue, _("Romania"))
    sk = Country(Belligerents.blue, _("Slovakia"))
    su = Country(Belligerents.red, _("Soviet Union"))
    uk = Country(Belligerents.red, _("United Kingdom"))
    us = Country(Belligerents.red, _("United States"))

    @classmethod
    def filter_by_belligerent(cls, belligerent):
        return filter(lambda x: x.belligerent == belligerent, cls.constants())


class AirForce(VerboseValueConstant):

    def __init__(self, country, default_flight_prefix, value,
                 verbose_name=None, help_text=None):
        super(AirForce, self).__init__(value,
                                       verbose_name=verbose_name,
                                       help_text=help_text)
        self.country = country

        if default_flight_prefix is not None:
            self.default_flight_prefix = str(default_flight_prefix)
        else:
            self.default_flight_prefix = None

    def merge_into_group(self, group):
        super(AirForce, self).merge_into_group(group)
        group.country = self.country
        group.default_flight_prefix = self.default_flight_prefix


class AirForces(with_constant_class(AirForce), Values):
    ala = AirForce(
        country=Countries.fr,
        default_flight_prefix='fr01',
        value='fr',
        verbose_name=_("ALA"),
        help_text=_("Army of the Air"),
    )
    faf = AirForce(
        country=Countries.fi,
        default_flight_prefix='f01',
        value='fi',
        verbose_name=_("FAF"),
        help_text=_("Finnish Air Force"),
    )
    far = AirForce(
        country=Countries.ro,
        default_flight_prefix='ro01',
        value='ro',
        verbose_name=_("FAR"),
        help_text=_("Romanian Air Force"),
    )
    haf = AirForce(
        country=Countries.hu,
        default_flight_prefix='h01',
        value='hu',
        verbose_name=_("HAF"),
        help_text=_("Hungarian Air Force"),
    )
    luftwaffe = AirForce(
        country=Countries.de,
        default_flight_prefix='g01',
        value='de',
        verbose_name=_("Luftwaffe"),
    )
    ija = AirForce(
        country=Countries.jp,
        default_flight_prefix='ja01',
        value='ja',
        verbose_name=_("IJA"),
        help_text=_("Imperial Japanese Army"),
    )
    ijn = AirForce(
        country=Countries.jp,
        default_flight_prefix='IN_NN',
        value='in',
        verbose_name=_("IJN"),
        help_text=_("Imperial Japanese Navy"),
    )
    paf = AirForce(
        country=Countries.pl,
        default_flight_prefix='pl01',
        value='pl',
        verbose_name=_("PAF"),
        help_text=_("Polish Air Force"),
    )
    rai = AirForce(
        country=Countries.it,
        default_flight_prefix='i01',
        value='it',
        verbose_name=_("RAI"),
        help_text=_("Regia Aeronautica Italiana"),
    )
    raaf = AirForce(
        country=Countries.au,
        default_flight_prefix='RA_NN',
        value='ra',
        verbose_name=_("RAAF"),
        help_text=_("Royal Australian Air Force"),
    )
    raf = AirForce(
        country=Countries.uk,
        default_flight_prefix='gb01',
        value='gb',
        verbose_name=_("RAF"),
        help_text=_("Royal Air Force"),
    )
    rn = AirForce(
        country=Countries.uk,
        default_flight_prefix='RN_NN',
        value='rn',
        verbose_name=_("RN"),
        help_text=_("Royal Navy"),
    )
    rnlaf = AirForce(
        country=Countries.nl,
        default_flight_prefix='DU_NN',
        value='du',
        verbose_name=_("RNLAF"),
        help_text=_("Royal Netherlands Air Force"),
    )
    rnzaf = AirForce(
        country=Countries.nz,
        default_flight_prefix='RZ_NN',
        value='rz',
        verbose_name=_("RNZAF"),
        help_text=_("Royal New Zealand Air Force"),
    )
    saf = AirForce(
        country=Countries.sk,
        default_flight_prefix='sk01',
        value='sk',
        verbose_name=_("SAF"),
        help_text=_("Slovak Air Force"),
    )
    usaaf = AirForce(
        country=Countries.us,
        default_flight_prefix='usa01',
        value='us',
        verbose_name=_("USAAF"),
        help_text=_("United States Army Air Forces"),
    )
    usmc = AirForce(
        country=Countries.us,
        default_flight_prefix='UM_NN',
        value='um',
        verbose_name=_("USMC"),
        help_text=_("United States Marine Corps"),
    )
    usn = AirForce(
        country=Countries.us,
        default_flight_prefix='UN_NN',
        value='un',
        verbose_name=_("USN"),
        help_text=_("United States Navy"),
    )
    vvs_rkka = AirForce(
        country=Countries.su,
        default_flight_prefix='r01',
        value='ru',
        verbose_name=_("VVS RKKA"),
        help_text=_("Workers-Peasants Red Army Air Forces"),
    )
    none = AirForce(
        country=None,
        default_flight_prefix=None,
        value='nn',
        verbose_name=_("None"),
    )

    @classmethod
    def get_flight_prefixes(cls):
        result = map(lambda x: x.default_flight_prefix, cls.iterconstants())
        if six.PY3:
            result = list(result)
        return result

    @classmethod
    def get_by_flight_prefix(cls, prefix):
        for constant in cls.iterconstants():
            if constant.default_flight_prefix == prefix:
                return constant
        raise ValueError(
            "Air force with prefix '{0}' is not present in '{1}'"
            .format(prefix, cls.__name__)
        )

    @classmethod
    def filter_by_country(cls, country):
        return filter(lambda x: x.country == country, cls.constants())

    @classmethod
    def filter_by_belligerent(cls, belligerent):
        return filter(
            lambda x: x.country.belligerent == belligerent if x.country else False,
            cls.constants()
        )


def _get_data_file_path(file_name):
    root = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(root, 'data', file_name)


class Regiment(object):

    def __init__(self, air_force, code_name):
        self.air_force = air_force
        self.code_name = str(code_name)

    def __getattr__(self, name):
        try:
            return super(Regiment, self).__getattr__(name)
        except AttributeError:
            if name.startswith('verbose_name_'):
                getter = self._get_verbose_name
                default_name_prefix = 'verbose_name'
            elif name.startswith('help_text_'):
                getter = self._get_help_text
                default_name_prefix = 'help_text'
            else:
                raise

        # Get language code
        start = name.rindex('_') + 1
        language_code = name[start:]
        if not language_code:
            raise AttributeError(
                "'{0}' object has no attribute '{1}'"
                .format(self.__class__.__name__, name)
            )

        # Check language code is known
        default_language_code = SupportedLanguages.get_default().name
        if not language_code in SupportedLanguages:
            language_code = default_language_code

        # Try to get value for specified language or for default language
        value = getter(language_code)
        if not value and language_code != default_language_code:
            default_name = '{0}_{1}'.format(default_name_prefix,
                                            default_language_code)
            value = getattr(self, default_name)

        # Add missing attribute to object
        setattr(self, name, value)
        return value

    def _get_verbose_name(self, language_code):
        file_name = "regShort_{0}.properties".format(language_code)
        return self._get_text(language_code, file_name)

    def _get_help_text(self, language_code):
        file_name = "regInfo_{0}.properties".format(language_code)
        return self._get_text(language_code, file_name)

    def _get_text(self, language_code, file_name):
        file_path = _get_data_file_path(file_name)

        with open(file_path, mode='r', encoding='cp1251') as f:
            for line in f:
                if line.startswith(self.code_name):
                    start = len(self.code_name)
                    result = line[start:].strip()
                    if six.PY3:
                        result = bytes(result, 'ascii')
                    return result.decode('unicode-escape')
        return ''

    def __repr__(self):
        return "<Regiment '{:}'>".format(self.code_name)


class Regiments(object):

    _cache = {}
    _file_name = 'regiments.ini'

    def __new__(cls):
        raise TypeError("'{0}' may not be instantiated".format(cls.__name__))

    @classmethod
    def get_by_code_name(cls, code_name):
        if code_name in cls._cache:
            return cls._cache[code_name]

        flight_prefixes = AirForces.get_flight_prefixes()
        last_flight_prefix = None
        found = False

        file_path = _get_data_file_path(cls._file_name)
        with open(file_path, mode='r', encoding='cp1251') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if line in flight_prefixes:
                    last_flight_prefix = line
                    continue
                if line == code_name:
                    found = True
                    break

        if found and last_flight_prefix:
            air_force = AirForces.get_by_flight_prefix(last_flight_prefix)
            regiment = Regiment(air_force, code_name)
            cls._cache[code_name] = regiment
            return regiment

        raise ValueError(
            "Regiment with code name '{0}' is unknown".format(code_name))

    @classmethod
    def filter_by_air_force(cls, air_force):
        result = []

        flight_prefixes = AirForces.get_flight_prefixes()
        found = False

        file_path = _get_data_file_path(cls._file_name)
        with open(file_path, mode='r', encoding='cp1251') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if line == air_force.default_flight_prefix:
                    # Flag that proper section was found.
                    found = True
                    continue
                if found:
                    if (
                        line in flight_prefixes
                        or (line.startswith('[') and line.endswith(']'))
                    ):
                        # Next section was found. Fullstop.
                        break

                    if line in cls._cache:
                        regiment = cls._cache[line]
                    else:
                        regiment = Regiment(air_force, line)
                        cls._cache[line] = regiment

                    result.append(regiment)
        return result
