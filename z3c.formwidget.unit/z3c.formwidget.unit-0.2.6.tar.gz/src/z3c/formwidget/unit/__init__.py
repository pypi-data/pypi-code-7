"""A multi unit widget for z3c.form."""

# python imports
from pint import UnitRegistry
import os

ureg = UnitRegistry()
ureg.load_definitions(
    os.path.join(os.path.dirname(__file__), 'pint_units.txt')
)
