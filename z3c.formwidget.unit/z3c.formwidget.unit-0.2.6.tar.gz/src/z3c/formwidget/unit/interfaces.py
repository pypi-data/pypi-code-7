# -*- coding: utf-8 -*-

# python imports
from decimal import Decimal

# zope imports
from z3c.form.interfaces import ITextWidget

# local imports
from z3c.formwidget.unit.i18n import _


TWOPLACES = Decimal(10) ** -2

SYSTEM_METRIC = 'metric'
SYSTEM_IMPERIAL = 'imperial'

DIMENSION_AREA = 'area'
DIMENSION_LENGTH = 'length'

UNIT_NONE = (None, None, None, None)

# Metric length units.
UNIT_MM = ('mm', u'mm', _(u'millimeter'), _(u'0.001 meter'))
UNIT_M = ('m', u'm', _(u'meter'), None)
UNIT_KM = ('km', u'km', _(u'kilometer'), _(u'1,000 meter'))

# Metric area units.
UNIT_SQM = ('sq_m', u'm²', _(u'square meter'), None)
UNIT_HA = ('ha', u'ha', _(u'hectare'), _(u'10,000 square meter'))
UNIT_SQKM = ('sq_km', u'km²', _(u'square kilometer'), _(u'100 hectare'))

# Imperial length units.
UNIT_IN = ('in', u'in', _(u'inch'), _(u'1/12 foot'))
UNIT_FT = ('ft', u'ft', _(u'foot'), None)
UNIT_YD = ('yd', u'yd', _(u'yard'), _(u'3 feet'))
UNIT_MI = ('mi', u'mi', _(u'mile'), _(u'1,760 yards'))

# Imperial area units.
UNIT_SQFT = ('sq_ft', u'sq ft', _(u'square feet'), None)
UNIT_ACRE = ('acre', u'acre', _(u'acre'), _(u'43,560 square feet'))
UNIT_SQMI = ('sq_mi', u'sq mi', _(u'square mile'), _(u'640 acres'))

LABELS = {
    SYSTEM_METRIC: _(u'Metric'),
    SYSTEM_IMPERIAL: _(u'Imperial'),
}

ALL_UNITS = [
    UNIT_ACRE,
    UNIT_FT,
    UNIT_HA,
    UNIT_IN,
    UNIT_KM,
    UNIT_M,
    UNIT_MI,
    UNIT_MM,
    UNIT_SQFT,
    UNIT_SQKM,
    UNIT_SQM,
    UNIT_SQMI,
    UNIT_YD,
]

UNITS = {
    SYSTEM_METRIC: {
        DIMENSION_AREA: [
            UNIT_SQM,  # level 0
            UNIT_HA,  # level 1
            UNIT_SQKM,  # level 2
        ],
        DIMENSION_LENGTH: [
            UNIT_MM,  # level 0
            UNIT_M,  # level 1
            UNIT_KM,  # level 2
        ],
    },
    SYSTEM_IMPERIAL: {
        DIMENSION_AREA: [
            UNIT_SQFT,  # level 0
            UNIT_ACRE,  # level 1
            UNIT_SQMI,  # level 2
        ],
        DIMENSION_LENGTH: [
            UNIT_IN,  # level 0
            UNIT_FT,  # level 1
            UNIT_MI,  # level 2
        ],
    },
}

METRICS = [
    UNIT_MM[0],
    UNIT_M[0],
    UNIT_KM[0],
    UNIT_SQM[0],
    UNIT_HA[0],
    UNIT_SQKM[0],
]

IMPERIALS = [
    UNIT_IN[0],
    UNIT_FT[0],
    UNIT_MI[0],
    UNIT_SQFT[0],
    UNIT_ACRE[0],
    UNIT_SQMI[0],
]


class IUnitWidget(ITextWidget):
    """Base unit widget."""


class ILengthWidget(IUnitWidget):
    """Unit widget for 'lenght' dimensions."""


class IAreaWidget(IUnitWidget):
    """Unit widget for 'area' dimensions."""
