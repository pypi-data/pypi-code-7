import re
from copy import copy
from z3c.form import group, field


spaces = r'\s'


class BaseGroup(group.Group):
    """ A generic group to use with form groups. Groups are preferrable to
    formsets on the mainform as the access to fields and widgets is much
    clearer. For example:

    class GeneralGroup(BaseGroup):
        label = _(u'General')
        group_fields = [
            [IEvent, ['start', 'end']
        ]

    class Form(BaseForm):
        groups = (GeneralGroup, )
        enable_form_tabbing = True

    You can also add more than one interface to the group_fields. For example:

    group_fields = [
        [IEvent, ['start', 'end']]
        [ILocation, ['lat', 'long']]
    ]

    Note that in this case you might have to write your own handle_save code
    in the form. The default handle_save code will only work if only one
    Interface is used (in one or over many groups).

    """

    @property
    def __name__(self):
        return re.sub(spaces, u'_', self.label.lower())

    @property
    def group_fields(self):
        raise NotImplementedError

    @property
    def fields(self):
        """ Returns the fields defined in group_fields, shallow copying all
        fields before they are returned so they can be safely manipulated.

        It is important that they are copied since these changes otherwise
        leak through to other forms.

        """

        if hasattr(self, '_cached_fields'):
            return self._cached_fields

        result = None

        for interface, fields in self.group_fields:
            if result is None:
                result = field.Fields(interface).select(*fields)
            else:
                result += field.Fields(interface).select(*fields)

            for f in fields:
                result[f].field = copy(result[f].field)

        self._cached_fields = result
        return result

    def updateWidgets(self):
        self.update_fields()
        super(BaseGroup, self).updateWidgets()
        self.update_widgets()

    def update_fields(self):
        """ Called when it's time to make changes to the fields. """

    def update_widgets(self):
        """ Called when it's time to make changes to the widgets. """
