from django.forms import DateField

from widgets import DatePickerInput


class DatePickerField(DateField):
    widget = DatePickerInput

    def __init__(self, widget=None, input_formats=None, picker_options=None, *args, **kwargs):
        widget = widget or self.widget

        # create widget instance with format and options applied
        if isinstance(widget, type) and input_formats:
            assert isinstance(input_formats, list)

            widget = widget(format=input_formats[0], options=picker_options)

        super(DatePickerField, self).__init__(widget=widget, input_formats=input_formats, *args, **kwargs)
