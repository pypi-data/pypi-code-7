# -*- coding: utf-8 -*-

from candv import Values, VerboseValueConstant

from .utils import translations


_ = translations.ugettext_lazy


class TargetTypes(Values):
    destroy = VerboseValueConstant(0, _("destroy"))
    destroy_area = VerboseValueConstant(1, _("destroy area"))
    destroy_bridge = VerboseValueConstant(2, _("destroy bridge"))
    recon = VerboseValueConstant(3, _("recon"))
    escort = VerboseValueConstant(4, _("escort"))
    cover = VerboseValueConstant(5, _("cover"))
    cover_area = VerboseValueConstant(6, _("cover area"))
    cover_bridge = VerboseValueConstant(7, _("cover bridge"))


class TargetPriorities(Values):
    primary = VerboseValueConstant(0, _("primary"))
    secondary = VerboseValueConstant(1, _("secondary"))
    hidden = VerboseValueConstant(2, _("hidden"))
