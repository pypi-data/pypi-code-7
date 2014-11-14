# -*- coding: utf-8 -*-

# python imports
from decimal import Decimal
from pint import UndefinedUnitError
import string

# fanstatic
try:
    from js.bootstrap_select import bootstrap_select
    HAS_BS_SELECT = True
except ImportError:
    HAS_BS_SELECT = False

# zope imports
from persistent.dict import PersistentDict
from z3c.form.widget import FieldWidget
from z3c.form.browser.text import TextWidget
from z3c.form.interfaces import (
    IDataConverter,
    IFieldWidget,
    IFormLayer,
    NO_VALUE,
)
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter
from zope.i18n import translate
from zope.security.proxy import Proxy, removeSecurityProxy
from zope.interface import (
    implementer,
    implementsOnly,
)
from zope.schema.interfaces import ITextLine

# local imports
from z3c.formwidget.unit import interfaces, ureg, utils
from z3c.formwidget.unit.i18n import _


KEY = 'z3c.formwidget.unit'


class MultiUnitWidget(TextWidget):
    """Multi Unit Widget based on TextWidget."""
    implementsOnly(interfaces.IUnitWidget)

    klass = u'multiunit-widget'
    value = u''
    unit = None

    unit_systems = (
        interfaces.SYSTEM_METRIC,
        interfaces.SYSTEM_IMPERIAL,
    )
    preferred_system = interfaces.SYSTEM_METRIC
    level_min = 0
    level_max = None

    data_header = _(u'Select a unit')
    data_width = '75px'

    _javascript_input = """
jQuery(function(jq){
  if (jQuery().selectpicker) {
    jq('#${id}-unit').selectpicker({});
  }
});
    """

    @property
    def unit_dimension(self):
        raise NotImplementedError

    @property
    def widget_value(self):
        """Return the converted value."""
        self.unit = self.request.get(self.name + '-unit', self.preferred_unit)
        if not self.value:
            return

        try:
            base_unit = getattr(ureg, self.base_unit)
        except UndefinedUnitError:
            value = self.value
        else:
            # Do the conversion
            converter = IDataConverter(self)
            try:
                value = converter.toFieldValue(self.value)
            except:
                return self.value
            system = None
            if not self.ignoreContext:
                system = self._get_unit_annotation()
            else:
                if self.unit in interfaces.METRICS:
                    system = interfaces.SYSTEM_METRIC
                elif self.unit in interfaces.IMPERIALS:
                    system = interfaces.SYSTEM_IMPERIAL
            if not system in self.unit_systems:
                system = self.preferred_system
            self.unit = utils.get_best_unit(
                value,
                system,
                self.unit_dimension,
                level_min=self.level_min,
                level_max=self.level_max,
            )[0]
            unit = getattr(ureg, self.unit)
            value = value * base_unit
            value = value.to(unit).magnitude
            if isinstance(value, Decimal):
                value = value.quantize(interfaces.TWOPLACES)
            value = converter.toWidgetValue(value)
        return value

    def render(self):
        if HAS_BS_SELECT:
            bootstrap_select.need()
        return super(MultiUnitWidget, self).render()

    def extract(self, default=NO_VALUE):
        value = self.request.get(self.name, default)
        converter = IDataConverter(self)
        try:
            c_value = converter.toFieldValue(value)
        except:
            return value

        unit_name = self.request.get(self.name + '-unit')
        if unit_name and unit_name != self.base_unit:
            try:
                unit = getattr(ureg, unit_name)
                base_unit = getattr(ureg, self.base_unit)
            except UndefinedUnitError:
                c_value = self.field.get(self.context)

            # Do the conversion
            try:
                c_value = c_value * unit
            except TypeError:
                return value
            else:
                c_value = c_value.to(base_unit).magnitude
            if not self.ignoreContext:
                self._set_unit_annotation(unit_name)
            value = converter.toWidgetValue(c_value)

        return value

    def _get_unit_annotation(self):
        context = self.context
        if isinstance(context, Proxy):
            context = removeSecurityProxy(context)
        try:
            annotations = IAnnotations(context)
        except:
            return None
        else:
            storage = annotations.get(KEY, {})
            return storage.get(self.name)

    def _set_unit_annotation(self, unit):
        context = self.context
        if isinstance(context, Proxy):
            context = removeSecurityProxy(context)
        try:
            annotations = IAnnotations(context)
        except:
            return None
        else:
            storage = annotations.get(KEY)
            if storage is None:
                storage = annotations[KEY] = PersistentDict({})
            # Store the unit system
            storage[self.name] = utils.system_for_unit(unit)

    def javascript_input(self):
        return string.Template(self._javascript_input).substitute(dict(
            id=self.id,
        ))

    def isSelected(self, key):
        return key == self.unit

    @property
    def base_unit(self):
        raise NotImplementedError

    @property
    def preferred_unit(self):
        return interfaces.UNITS.get(
            self.preferred_system, {}
        ).get(self.unit_dimension, [(None,)])[0][0]

    def items(self):
        items = []
        for system in self.unit_systems:
            dimensions = interfaces.UNITS.get(system, None)
            if not dimensions:
                continue
            units = []
            available_units = dimensions.get(self.unit_dimension, [])
            if self.level_max is not None:
                level_max = self.level_max + 1
            else:
                level_max = None
            available_units = available_units[self.level_min:level_max]
            for unit in available_units:
                abbr, label_short, label, info = unit
                subtext = translate(label, context=self.request)
                if info:
                    info = translate(info, context=self.request)
                    subtext = subtext + ' (%s)' % info
                units.append({
                    'id': abbr,
                    'value': abbr,
                    'content': label_short,
                    'subtext': subtext,
                    'selected': self.isSelected(abbr),
                })

            item = {}
            item['title'] = interfaces.LABELS.get(system)
            item['member'] = units
            items.append(item)

        return items

    def unit_label(self):
        unit = [unit for unit in interfaces.ALL_UNITS if unit[0] == self.unit]
        unit = unit and unit.pop() or interfaces.UNIT_NONE
        return unit[1]


class AreaWidget(MultiUnitWidget):
    """Unit widget for 'area' dimensions."""
    implementsOnly(interfaces.IAreaWidget)
    klass = u'area-widget unit-widget'

    @property
    def unit_dimension(self):
        return interfaces.DIMENSION_AREA

    @property
    def base_unit(self):
        return interfaces.UNIT_SQM[0]


@adapter(ITextLine, IFormLayer)
@implementer(IFieldWidget)
def AreaFieldWidget(field, request):
    """Factory for AreaWidget"""
    return FieldWidget(field, AreaWidget(request))


class LengthWidget(MultiUnitWidget):
    """Unit widget for 'length' dimensions."""
    implementsOnly(interfaces.ILengthWidget)
    klass = u'length-widget unit-widget'

    @property
    def unit_dimension(self):
        return interfaces.DIMENSION_LENGTH

    @property
    def base_unit(self):
        return interfaces.UNIT_M[0]


@adapter(ITextLine, IFormLayer)
@implementer(IFieldWidget)
def LengthFieldWidget(field, request):
    """Factory for LengthWidget"""
    return FieldWidget(field, LengthWidget(request))
