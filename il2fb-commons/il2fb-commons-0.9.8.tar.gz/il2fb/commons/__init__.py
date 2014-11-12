# -*- coding: utf-8 -*-

from candv import (
    SimpleConstant, Constants, Values, ValueConstant, VerboseValueConstant,
)

from .utils import translations


_ = translations.ugettext_lazy


class SupportedLanguages(Constants):
    en = SimpleConstant()
    ru = SimpleConstant()

    @classmethod
    def get_default(cls):
        return cls.en


class GameVersions(Values):
    v4_12 = ValueConstant('4.12')
    v4_12_1 = ValueConstant('4.12.1')
    v4_12_2 = ValueConstant('4.12.2')

    @classmethod
    def get_default(cls):
        return cls.constants()[-1]


class Skills(Values):
    rookie = VerboseValueConstant(0, _("rookie"))
    average = VerboseValueConstant(1, _("average"))
    veteran = VerboseValueConstant(2, _("veteran"))
    ace = VerboseValueConstant(3, _("ace"))


class UnitTypes(Values):
    aircraft = VerboseValueConstant('planes', _("aircraft"))
    armor = VerboseValueConstant('armor', _("armor"))
    artillery = VerboseValueConstant('artillery', _("artillery"))
    balloon = VerboseValueConstant('aeronautics', _("balloon"))
    light = VerboseValueConstant('lights', _("light"))
    radio = VerboseValueConstant('radios', _("radio"))
    ship = VerboseValueConstant('ships', _("ship"))
    stationary = VerboseValueConstant('stationary', _("stationary"))
    train = VerboseValueConstant('trains', _("train"))
    vehicle = VerboseValueConstant('vehicles', _("vehicle"))
