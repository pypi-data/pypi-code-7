# -*- coding: utf-8 -*-

from candv import Values, VerboseValueConstant

from .utils import translations


_ = translations.ugettext_lazy


class Formations(Values):
    echelon_right = VerboseValueConstant('F2', _("echelon right"))
    echelon_left = VerboseValueConstant('F3', _("echelon left"))
    line_abreast = VerboseValueConstant('F4', _("line abreast"))
    line_asteam = VerboseValueConstant('F5', _("line asteam"))
    vic = VerboseValueConstant('F6', _("vic"))
    finger_four = VerboseValueConstant('F7', _("finger four"))
    diamond = VerboseValueConstant('F8', _("diamond"))


class RoutePointTypes(Values):
    # Take-off ----------------------------------------------------------------
    takeoff_normal = VerboseValueConstant(
        'TAKEOFF',
        _("takeoff (normal)"))
    takeoff_pair = VerboseValueConstant(
        'TAKEOFF_002',
        _("takeoff (pair)"))
    takeoff_in_line = VerboseValueConstant(
        'TAKEOFF_003',
        _("takeoff (in line)"))
    takeoff_taxiing = VerboseValueConstant(
        'TAKEOFF_004',
        _("takeoff (taxiing)"))

    # Normal flight -----------------------------------------------------------
    normal = VerboseValueConstant(
        'NORMFLY',
        _("normal"))

    # Attack ------------------------------------------------------------------
    #: .. warning::
    #:   air attack is not present in game. It is calculated as ``NORMFLY``
    #:   with a target
    air_attack = VerboseValueConstant(
        'X_AIR_ATTACK',
        _("air attack"))
    ground_attack = VerboseValueConstant(
        'GATTACK',
        _("ground attack"))

    # Patrol ------------------------------------------------------------------
    patrol_triangle = VerboseValueConstant(
        'NORMFLY_401',
        _("patrol (triangle)"))
    patrol_square = VerboseValueConstant(
        'NORMFLY_402',
        _("patrol (square)"))
    patrol_pentagon = VerboseValueConstant(
        'NORMFLY_403',
        _("patrol (pentagon)"))
    patrol_hexagon = VerboseValueConstant(
        'NORMFLY_404',
        _("patrol (hexagon)"))
    patrol_random = VerboseValueConstant(
        'NORMFLY_405',
        _("patrol (random)"))

    # Artillery spotter -------------------------------------------------------
    artillery_spotter = VerboseValueConstant(
        'NORMFLY_407',
        _("artillery spotter"))

    # Langing -----------------------------------------------------------------
    landing_on_left = VerboseValueConstant(
        'LANDING',
        _("landing (on left)"))
    landing_on_right = VerboseValueConstant(
        'LANDING_101',
        _("landing (on right)"))
    landing_short_on_left = VerboseValueConstant(
        'LANDING_102',
        _("landing (short on left)"))
    landing_short_on_right = VerboseValueConstant(
        'LANDING_103',
        _("landing (short on right)"))
    landing_straight = VerboseValueConstant(
        'LANDING_104',
        _("landing (straight)"))
