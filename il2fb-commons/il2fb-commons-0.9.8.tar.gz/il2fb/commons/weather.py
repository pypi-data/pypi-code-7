# -*- coding: utf-8 -*-

from candv import Values, VerboseValueConstant

from .utils import translations


_ = translations.ugettext_lazy


class Conditions(Values):
    clear = VerboseValueConstant(0, _("clear"))
    good = VerboseValueConstant(1, _("good"))
    hazy = VerboseValueConstant(2, _("hazy"))
    poor = VerboseValueConstant(3, _("poor"))
    blind = VerboseValueConstant(4, _("blind"))
    precipitation = VerboseValueConstant(5, _("precipitation"))
    thunderstorm = VerboseValueConstant(6, _("thunderstorm"))


class Gust(Values):
    none = VerboseValueConstant(0, _("none"))
    low = VerboseValueConstant(1, _("low_gust"))
    moderate = VerboseValueConstant(2, _("moderate_gust"))
    strong = VerboseValueConstant(3, _("strong_gust"))


class Turbulence(Values):
    none = VerboseValueConstant(0, _("none"))
    low = VerboseValueConstant(1, _("low_turbulence"))
    moderate = VerboseValueConstant(2, _("moderate_turbulence"))
    strong = VerboseValueConstant(3, _("strong_turbulence"))
    very_strong = VerboseValueConstant(4, _("very_strong_turbulence"))
