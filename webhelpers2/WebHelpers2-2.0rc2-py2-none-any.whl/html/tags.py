"""Helpers that produce simple HTML tags.

Most helpers have an ``**attrs`` argument to specify additional HTML
attributes.  A trailing underscore in the name will be deleted; this is 
especially important for attributes that are identical to Python keywords;
e.g., ``class_``.  Some helpers handle certain keywords specially; these are
noted in the helpers' docstrings.

To create your own custom tags, see ``webhelpers2.html.builder``.
"""

from __future__ import unicode_literals
import datetime
import logging
import os
import re

import six

from webhelpers2 import containers
from webhelpers2.html import escape, HTML, literal, url_escape
from webhelpers2.misc import NotGiven

__all__ = [
           # Form tags
           "form", "end_form", 
           "text", "textarea", "hidden", "file", "password", 
           "checkbox", "radio", "submit",
           "select", "Options", "Option", "OptGroup", "SelectedValues",
           "ModelTags",
           # hyperlinks
           "link_to", "link_to_if", "link_to_unless",
           # Table tags
           "th_sortable",
           # Other non-form tags
           "ol", "ul", "image",
           # Head tags and document type
           "stylesheet_link", "javascript_link", "auto_discovery_link",
           # Lazy-rendering tags
           "Link",
           # Backward compatibility
           "BR",
           ]

log = logging.getLogger(__name__)


########## Function-based form tag helpers ##########

def form(url, method="post", multipart=False, hidden_fields=None, **attrs):
    """An open tag for a form that will submit to ``url``.

    You must close the form yourself by calling ``end_form()`` or outputting
    </form>.
    
    Options:

    ``method``
        The method to use when submitting the form, usually either 
        "GET" or "POST". If "PUT", "DELETE", or another verb is used, a
        hidden input with name _method is added to simulate the verb
        over POST.
    
    ``multipart``
        If set to True, the enctype is set to "multipart/form-data".
        You must set it to true when uploading files, or the browser will
        submit the filename rather than the file.

    ``hidden_fields``
        Additional hidden fields to add to the beginning of the form.  It may
        be a dict or an iterable of key-value tuples. This is implemented by
        calling the object's ``.items()`` method if it has one, or just
        iterating the object.  (This will successfuly get multiple values for
        the same key in WebOb MultiDict objects.)

    Because input tags must be placed in a block tag rather than directly
    inside the form, all hidden fields will be put in a 
    '<div style="display:none">'.  The style prevents the <div> from being
    displayed or affecting the layout.
    """
    fields = []
    attrs["action"] = url
    if multipart:
        attrs["enctype"] = "multipart/form-data"
    if method.lower() in ['post', 'get']:
        attrs['method'] = method
    else:
        attrs['method'] = "post"
        field = hidden("_method", method, id=None)
        fields.append(field)
    if hidden_fields is not None:
        try:
            it = hidden_fields.items()
        except AttributeError:
            it = hidden_fields
        for name, value in it:
            field = hidden(name, value, id=None)
            fields.append(field)
    if fields:
        div = HTML.tag("div", style="display:none", _nl=True, *fields)
    else:
        div = None
    return HTML.tag("form", div, _closed=False, **attrs)


def end_form():
    """Output "</form>".
    """
    return literal("</form>")


def text(name, value=None, id=NotGiven, type="text", **attrs):
    """Create a standard text field.
    
    ``value`` is a string, the content of the text field.

    ``id`` is the HTML ID attribute, and should be passed as a keyword
    argument.  By default the ID is the same as the name filtered through
    ``_make_safe_id_component()``.  Pass None to suppress the
    ID attribute entirely.

    ``type`` is the input field type, normally "text". You can override it
    for HTML 5 input fields that don't have their own helper; e.g.,
    "search", "email", "date".

    
    Options:
    
    * ``disabled`` - If set to True, the user will not be able to use
        this input.
    * ``size`` - The number of visible characters that will fit in the
        input.
    * ``maxlength`` - The maximum number of characters that the browser
        will allow the user to enter.
    
    The remaining keyword args will be standard HTML attributes for the tag.
    """
    return _input(type, name, value, id, attrs)


def hidden(name, value=None, id=NotGiven, **attrs):
    """Create a hidden field.
    """
    return _input("hidden", name, value, id, attrs)


def file(name, value=None, id=NotGiven, **attrs):
    """Create a file upload field.
    
    If you are using file uploads then you will also need to set the 
    multipart option for the form.

    Example::

        >>> file('myfile')
        literal(u'<input id="myfile" name="myfile" type="file" />')
    
    """
    return _input("file", name, value, id, attrs)


def password(name, value=None, id=NotGiven, **attrs):
    """Create a password field.
    
    Takes the same options as ``text()``.
    
    """
    return _input("password", name, value, id, attrs)


def textarea(name, content="", id=NotGiven, **attrs):
    """Create a text input area.
    """
    attrs["name"] = name
    _set_id_attr(attrs, id, name)
    return HTML.tag("textarea", content, **attrs)


def checkbox(name, value="1", checked=False, label=None, label_class=None,
    id=NotGiven, **attrs):
    """Create a check box.

    Arguments:
    ``name`` -- the widget's name.

    ``value`` -- the value to return to the application if the box is checked.

    ``checked`` -- true if the box should be initially checked.

    ``label`` -- a text label to display to the right of the box.
    This puts a <label> tag around the input tag.

    ``label_class`` -- CSS class for <label> tag. This should be a keyword
    argument because its position may change in a future version.

    ``id`` is the HTML ID attribute, and should be passed as a keyword
    argument.  By default the ID is the same as the name filtered through
    ``_make_safe_id_component()``.  Pass None to suppress the
    ID attribute entirely.

    The following HTML attributes may be set by keyword argument:

    * ``disabled`` - If true, checkbox will be grayed out.

    * ``readonly`` - If true, the user will not be able to modify the checkbox.

    To arrange multiple checkboxes in a group, see
    webhelpers2.containers.distribute().
    """
    if checked:
        attrs["checked"] = "checked"
    widget = _input("checkbox", name, value, id, attrs)
    if label:
        widget = HTML.tag("label", widget, " ", label, class_=label_class)
    return widget

def radio(name, value, checked=False, label=None, label_class=None, **attrs):
    """Create a radio button.

    Arguments:
    ``name`` -- the field's name.

    ``value`` -- the value returned to the application if the button is
    pressed.

    ``checked`` -- true if the button should be initially pressed.

    ``label`` -- a text label to display to the right of the button.
    This puts a <label> tag around the input tag.
    
    ``label_class`` -- CSS class for <label> tag. This should be a keyword
    argument because its position may change in a future version.

    The id of the radio button will be set to the name + '_' + value to 
    ensure its uniqueness.  An ``id`` keyword arg overrides this.  (Note
    that this behavior is unique to the ``radio()`` helper.)
    
    To arrange multiple radio buttons in a group, see
    webhelpers2.containers.distribute().
    """
    if checked:
        attrs["checked"] = "checked"
    if not "id" in attrs:
        attrs["id"] = "{0}_{1}".format(name, _make_safe_id_component(value))
    # Pass None as 'id' arg to '_input()' to prevent further modification of
    # the 'id' attribute.
    widget = _input("radio", name, value, None, attrs)
    if label:
        widget = HTML.tag("label", widget, " ", label, class_=label_class)
    return widget


def submit(name, value, id=NotGiven, **attrs):
    """Create a submit button with the text ``value`` as the caption."""
    return _input("submit", name, value, id, attrs)


def select(name, selected_values, options, id=NotGiven, **attrs):
    """Create a dropdown selection box.

    This is mostly a wrapper around the ``Options`` helper.

    Arguments:

    **name**: the name of this control.

    **selected_values**: the value(s) that should be preselected.
      See the ``SelectedValues`` class for the allowed types.

    **options**: an iterable of options. See the ``Options`` class
      for the allowed types.

    **id**: the HTML ID attribute. This should be a keyword argument if
      passed.  By default the ID is the same as the name.  filtered through
      ``_make_safe_id_component()``.  Pass None to suppress the
      ID attribute entirely.

    The following options may only be keyword arguments:

    **multiple**: if true, this control will allow multiple
       selections.

    **prompt**: An extra option that will be prepended to the list.
      The argument is the option label; e.g., "Please choose ...". The generated
      option's value will be the empty string (""), which is equivalent to not
      making a selection.

    Any other keyword args will become HTML attributes for the <select>.
    """

    _set_id_attr(attrs, id, name)
    attrs["name"] = name
    # Prepend the prompt
    prompt = attrs.pop("prompt", None)
    if prompt:
        options = [("", prompt)] + list(options)
    options = Options(options, selected_values)
    return HTML.tag("select", NL, options, **attrs)


########## Options helper and support classes ###########

class Options(object):
    """A list of options for a select or datalist.

    The constructor takes an iterable of diverse types and converts them to
    a list of ``Option`` and/or ``OptGroup`` instances. The list is available
    under the ``options`` attribute.

    My string representation is a concatenation of <option> and <optgroup> tags
    with a newline after each.  ``select()`` does this automatically, or you can
    manually render me in an HTML <select> or <datalist>. If an option's value
    is identical to its label, only the label will be rendered; see the
    ``Option`` class for examples.

    Constructor args:

    * **options**: An iterable whose elements are the type(s) in the next
      paragraph. Required.
    * **selected_values**: The value(s) that should be selected. See
      the ``SelectedValues`` class for the allowed types.

    The elements in the ``options`` iterable can be any of the following
    types:

    * An ``Option`` instance. It will be appended to ``self.options`` as-is.
    * An ``OptGroup`` instance. It will be appended to ``self.options`` as-is.
    * A scalar value. It will be converted to a string and used as both the
      option's value and label.
    * A sequence whose first two elements are a scalar value and a string.
      The first is the option value, the second is the option label.
    * A sequence whose first element is a non-string iteratable and second
      element is a string. This is converted to an ``OptGroup``. The first
      argument is recursively passed to me to create the group's options.
      The second argument becomes the group's label.

    If the ``options`` argument is already an ``Options`` instance,
    it is taken as-is without further processing.
    """

    def __init__(self, options, selected_values=None):
        if isinstance(options, self.__class__):
            self.options = options
            return
        self.options = []
        selected_values = SelectedValues(selected_values)
        text_type = six.text_type
        opts = []
        for opt in options:
            if isinstance(opt, (Option, OptGroup)):
                self.options.append(opt)
                continue
            if isinstance(opt, (list, tuple)):
                value, label = opt[:2]
                if isinstance(value, (list, tuple)):  # It's an optgroup
                    self.options.append(OptGroup(label, value))
                    continue
            else:
                value = label = opt
            if not isinstance(value, text_type):
                value = text_type(value)
            if not isinstance(label, text_type):  # Preserves literal.
                label = text_type(label)
            if value is not None:
                selected = value in selected_values
            else:
                selected = label in selected_values
            opt = Option(value, label, selected)
            self.options.append(opt)

    def __html__(self):
        return HTML(*self.options, nl=True)

    __str__ = __html__

    def __repr__(self):
        return _repr(self, self.options)

    def values(self):
        """Iterate the ``value`` attribute of all options.

        If the value is identical to the label it will appear here but it
        won't be rendered in the HTML.

        This method is intended only for flat option sequences, not groups. It
        will raise AttributeError if it encounters an ``OptGroup``.
        """
        return (x.value for x in self.options)

    def labels(self):
        """Iterate the ``label`` attribute of all options.

        This method is intended only for flat option sequences, not groups. It
        will yield the group label if it encounters an ``OptGroup``.
        """
        return (x.label for x in self.options)


class Option(object):
    """An option for an HTML select or datalist.

    The ``Options`` constructor calls me automatically.

    Attributes and constructor args:

    * **value**: The option value.
    * **label**: The option label.
    * **selected**: True if the option is selected. Default false.

    My string representation is an HTML <option> tag. If the value is None or
    identical to the label it will be suppressed, producing
    '<option>LABEL</option>'.  If the value is different from the label it
    produces '<option value="VALUE">LABEL</option>'.
    """

    __slots__ = ("value", "label", "selected")

    def __init__(self, value, label, selected=False):
        self.value = value
        self.label = label
        self.selected = selected

    def __html__(self):
        value = self.value
        label = self.label
        selected = self.selected
        if value == label:
            value = None
        text_type = six.text_type
        if value is not None and not isinstance(value, text_type):
            value = text_type(value)
        if not isinstance(label, text_type):  # Preserve literal.
            label = text_type(label)
        return HTML.tag("option", label, value=value, selected=selected)

    __str__ = __html__

    def __repr__(self):
        return _repr(self, self.value, self.label, self.selected)


class OptGroup(object):
    """An option group.

    The ``Options`` constructor calls me automatically.

    Attributes and constructor args:

    * **label**: The group label.
    * **options**: A list of options. This will be passed to ``Options``.

    My string representation is an HTML <optgroup> tag.
    """

    __slots__ = ('options', 'label')

    def __init__(self, label, options):
        self.options = Options(options)
        self.label = label

    def __html__(self):
        return HTML.tag("optgroup", NL, self.options, label=self.label)

    __str__ = __html__

    def __repr__(self):
        return _repr(self, self.label, self.options)


class SelectedValues(tuple):
    """A tuple subclass to manage the selected values for an options list.

    The ``Options`` constructor calls me automatically.

    My main purpose is to convert my constructor arg to a tuple of strings
    for the right side of ``x in selected_values`` expressions,
    and to avoid converting the same argument repeatedly.

    My constructor accepts the following types:

    * A scalar value. Converted to a string.
    * A non-string iterator. All elements are converted to strings.
    * An instance of myself. Taken as-is.
    * None. This imples the empty string ("") is selected.
    * A ``SelectedValues`` instance. Taken as-is.
    """

    def __new__(cls, values):
        if isinstance(values, cls):
            return values
        if values is None:
            values = ("",)
        elif isinstance(values, six.string_types) or \
            not hasattr(values, "__iter__"):
            values = (six.text_type(values),)
        else:
            values = tuple(map(six.text_type, values))
        return super(SelectedValues, cls).__new__(cls, values)


########## ModelTags helper ##########

class ModelTags(object):
    """A nice way to build a form for a database record.
    
    ModelTags allows you to build a create/update form easily.  (This is the
    C and U in CRUD.)  The constructor takes a database record, which can be
    a SQLAlchemy mapped class, or any object with attributes or keys for the
    field values.  Its methods shadow the the form field helpers, but it
    automatically fills in the value attribute based on the current value in
    the record.  (It also knows about the 'checked' and 'selected' attributes
    for certain tags.)

    You can also use the same form  to input a new record.  Pass ``None`` or
    ``""`` instead of a record, and it will set all the current values to a
    default value, which is either the `default` keyword arg to the method, or
    `""` if not specified.
    """

    undefined_values = set([None, ""])

    def __init__(self, record, use_keys=False, date_format="%m/%d/%Y", 
        id_format=None):
        """Create a ``ModelTags`` object.

        ``record`` is the database record to lookup values in.  It may be
        any object with attributes or keys, including a SQLAlchemy mapped
        instance.  It may also be ``None`` or ``""`` to indicate that a new
        record is being created.  (The class attribute ``undefined_values``
        tells which values indicate a new record.)

        If ``use_keys`` is true, values will be looked up by key.  If false
        (default), values will be looked up by attribute.

        ``date_format`` is a strftime-compatible string used by the ``.date``
        method.  The default is American format (MM/DD/YYYY), which is
        most often seen in text fields paired with popup calendars.
        European format (DD/MM/YYYY) is "%d/%m/%Y".  ISO format (YYYY-MM-DD)
        is "%Y-%m-%d".

        ``id_format`` is a formatting-operator format for the HTML 'id'
        attribute.  It should contain one "{}" where the tag's name will be
        embedded. For backward compatibility with WebHelpers, "%s" is
        automatically converted to "{}".
        """
        self.record = record
        self.use_keys = use_keys
        self.date_format = date_format
        if id_format:
            id_format = id_format.replace("%s", "{0}")
        self.id_format = id_format
    
    def checkbox(self, name, value='1', label=None, **kw):
        """Build a checkbox field.
        
        The box will be initially checked if the value of the corresponding
        database field is true.

        The submitted form value will be "1" if the box was checked. If the
        box is unchecked, no value will be submitted. (This is a downside of
        the standard checkbox tag.)

        To display multiple checkboxes in a group, see
        webhelper.containers.distribute().
        """
        self._update_id(name, kw)
        value = kw.pop("value", "1")
        checked = bool(self._get_value(name, kw))
        return checkbox(name, value, checked, label, **kw)

    def date(self, name, **kw):
        """Same as text but format a date value into a date string.

        The value can be a `datetime.date`, `datetime.datetime`, `None`,
        or `""`.  The former two are converted to a string using the
        date format passed to the constructor.  The latter two are converted
        to "".

        If there's no database record, consult keyword arg `default`. It it's
        the string "today", use todays's date. Otherwise it can be any of the
        values allowed above.  If no default is specified, the text field is
        initialized to "".

        Hint: you may wish to attach a Javascript calendar to the field.
        """
        self._update_id(name, kw)
        value = self._get_value(name, kw)
        if isinstance(value, datetime.date):
            value = value.strftime(self.date_format)
        elif value == "today":
            value = datetime.date.today().strftime(self.date_format)
        else:
            value = ""
        return text(name, value, **kw)

    def file(self, name, **kw):
        """Build a file upload field.
        
        User agents may or may not respect the contents of the 'value' attribute."""
        self._update_id(name, kw)
        value = self._get_value(name, kw)
        return file(name, value, **kw)

    def hidden(self, name, **kw):
        """Build a hidden HTML field."""
        self._update_id(name, kw)
        value = self._get_value(name, kw)
        return hidden(name, value, **kw)

    def password(self, name, **kw):
        """Build a password field.
        
        This is the same as a text box but the value will not be shown on the
        screen as the user types.
        """
        self._update_id(name, kw)
        value = self._get_value(name, kw)
        return password(name, value, **kw)

    def radio(self, name, checked_value, label=None, **kw):
        """Build a radio button.

        The radio button will initially be selected if the database value 
        equals ``checked_value``.  On form submission the value will be 
        ``checked_value`` if the button was selected, or ``""`` otherwise.

        In case of a ModelTags object that is created from scratch
        (e.g. ``new_employee=ModelTags(None)``) the option that should
        be checked can be set by the 'default' parameter. As in:
        ``new_employee.radio('status', checked_value=7, default=7)``

        The control's 'id' attribute will be modified as follows:

        1. If not specified but an 'id_format' was given to the constructor,
           generate an ID based on the format.
        2. If an ID was passed in or was generated by step (1), append an
           underscore and the checked value.  Before appending the checked
           value, lowercase it, change any spaces to ``"_"``, and remove any
           non-alphanumeric characters except underscores and hyphens.
        3. If no ID was passed or generated by step (1), the radio button 
           will not have an 'id' attribute.

        To display multiple radio buttons in a group, see
        webhelper.containers.distribute().
        """
        self._update_id(name, kw)
        value = self._get_value(name, kw)
        if 'id' in kw:
            kw["id"] = "{0}_{1}".format(kw['id'], _make_safe_id_component(checked_value))
        checked = (value == checked_value)
        return radio(name, checked_value, checked, label, **kw)

    def select(self, name, options, **kw):
        """Build a dropdown select box or list box.

        See the ``select()`` function for the meaning of the arguments.

        If the corresponding database value is not a list or tuple, it's
        wrapped in a one-element list.  But if it's "" or ``None``, an empty
        list is substituted.  This is to accommodate multiselect lists, which
        may have multiple values selected. """
        self._update_id(name, kw)
        selected_values = self._get_value(name, kw)
        return select(name, selected_values, options, **kw)

    def text(self, name, **kw):
        """Build a text box."""
        self._update_id(name, kw)
        value = self._get_value(name, kw)
        return text(name, value, **kw)

    def textarea(self, name, **kw):
        """Build a rectangular text area."""
        self._update_id(name, kw)
        content = self._get_value(name, kw)
        return textarea(name, content, **kw)

    # Private methods.
    def _get_value(self, name, kw):
        """Get the current value of a field from the database record.

        ``name``: The field to look up.

        ``kw``: The keyword args passed to the original method.  This is
        _not_ a "\*\*" argument!  It's a dict that will be modified in place!

        ``kw["default"]`` will be popped from the dict in all cases for
        possible use as a default value.  If the record doesn't exist, this
        default is returned, or ``""`` if no default was passed.
        """
        default = kw.pop("default", "")
        # This used to be ``self.record in self.undefined_values``, but this
        # fails if the record is a dict because dicts aren't hashable.
        for undefined_value in self.undefined_values:
            if self.record == undefined_value:
                return default
        if self.use_keys:
            return self.record[name]    # Raises KeyError.
        else:
            return getattr(self.record, name)   # Raises AttributeError.

    def _update_id(self, name, kw):
        """Apply the 'id' attribute algorithm.

        ``name``: The name of the HTML field.

        ``kw``: The keyword args passed to the original method.  This is
        _not_ a "\*\*" argument!  It's a dict that will be modified in place!

        If an ID format was specified but no 'id' keyword was passed, 
        set the 'id' attribute to a value generated from the format and name.
        Otherwise do nothing.
        """
        if self.id_format is not None and 'id' not in kw:
            kw['id'] = self.id_format.format(name)


########## Hyperlink tags ##########

def link_to(label, url='', **attrs):
    """Create a hyperlink with the given text pointing to the URL.
    
    If the label is ``None`` or empty, the URL will be used as the label.

    This function does not modify the URL in any way.  The label will be
    escaped if it contains HTML markup.  To prevent escaping, wrap the label
    in a ``webhelpers2.html.literal()``.
    """
    attrs['href'] = url
    if label == '' or label is None:
        label = url
    return HTML.tag("a", label, **attrs)


def link_to_if(condition, label, url='', **attrs):
    """Same as ``link_to`` but return just the label if the condition is false.
    
    This is useful in a menu when you don't want the current option to be a
    link.  The condition will be something like:
    ``actual_value != value_of_this_menu_item``.
    """
    if condition:
        return link_to(label, url, **attrs)
    else:
        return HTML(label)

def link_to_unless(condition, label, url='', **attrs):
    """The opposite of ``link_to``. Return just the label if the condition is 
    true.
    """
    if not condition:
        return link_to(label, url, **attrs)
    else:
        return HTML(label)


########## Table tags ##########

def th_sortable(current_order, column_order, label, url,
    class_if_sort_column="sort", class_if_not_sort_column=None, 
    link_attrs=None, name="th", **attrs):
    """<th> for a "click-to-sort-by" column.

    Convenience function for a sortable column.  If this is the current sort
    column, just display the label and set the cell's class to
    ``class_if_sort_column``.
    
    ``current_order`` is the table's current sort order.  ``column_order`` is
    the value pertaining to this column.  In other words, if the two are equal,
    the table is currently sorted by this column.

    If this is the sort column, display the label and set the <th>'s class to
    ``class_if_sort_column``.

    If this is not the sort column, display an <a> hyperlink based on
    ``label``, ``url``, and ``link_attrs`` (a dict), and set the <th>'s class
    to ``class_if_not_sort_column``.  
    
    ``url`` is the literal href= value for the link.  Pylons users would
    typically pass something like ``url=h.url_for("mypage", sort="date")``.

    ``**attrs`` are additional attributes for the <th> tag.

    If you prefer a <td> tag instead of <th>, pass ``name="td"``.

    To change the sort order via client-side Javascript, pass ``url=None`` and
    the appropriate Javascript attributes in ``link_attrs``.
    """
    from webhelpers2.html import HTML
    if current_order == column_order:
        content = label
        class_ = class_if_sort_column
    else:
        link_attrs = link_attrs or {}
        content = HTML.tag("a", label, href=url, **link_attrs)
        class_ = class_if_not_sort_column
    return HTML.tag("th", content, class_=class_, **attrs)



########## Other non-form tags ##########

def ul(items, default=None, li_attrs=None, **attrs):
    R"""Return an unordered list with each item wrapped in <li>.

    ``items``
        list of strings.

    ``default``
        value returned _instead of the <ul>_ if there are no items in the list.
        If ``None``, return an empty <ul>.

    ``li_attrs``
        dict of attributes for the <li> tags.
    """
    li_attrs = li_attrs or {}
    return _list("ul", items, default, attrs, li_attrs)

def ol(items, default=literal(""), li_attrs=None, **attrs):
    R"""Return an ordered list with each item wrapped in <li>.

    ``items``
        list of strings.

    ``default``
        value returned _instead of the <ol>_ if there are no items in the list.
        If ``None``, return an empty <ol>.

    ``li_attrs``
        dict of attributes for the <li> tags.
    """
    li_attrs = li_attrs or {}
    return _list("ol", items, default, attrs, li_attrs)

def _list(tag, items, default, attrs, li_attrs):
    content = [HTML.tag("li", x, **li_attrs) for x in items]
    if content:
        content = [""] + content + [""]
    elif default is not None:
        return default
    content = literal("\n").join(content)
    return HTML.tag(tag, content, **attrs)
    

def image(url, alt, width=None, height=None, **attrs):
    """Return an image tag for the specified ``source``.

    ``url``
        The URL of the image.  (This must be the exact URL desired.  A
        previous version of this helper added magic prefixes; this is
        no longer the case.)
    
    ``alt``
        The img's alt tag. Non-graphical browsers and screen readers will
        output this instead of the image.  If the image is pure decoration
        and uninteresting to non-graphical users, pass "".  To omit the
        alt tag completely, pass None.

    ``width``
        The width of the image, default is not included.

    ``height``
        The height of the image, default is not included.

    Note: This version does not support the 'path' and 'use_pil' arguments,
    because they depended on the WebHelpers 'media' subpackage which was
    dropped in WebHelpers 2. 
    """
    if "path" in attrs:
        raise TypeError("the 'path' arg is not supported in WebHelpers2")
    if "use_pil" in attrs:
        raise TypeError("the 'use_pil' arg is not supported in WebHelpers2")
    if not alt:
        alt = ""
    if width is not None or height is not None:
        attrs['width'] = width
        attrs['height'] = height
    return HTML.tag("img", src=url, alt=alt, **attrs)


########## Tags for the HTML head ##########

def javascript_link(*urls, **attrs):
    """Return script include tags for the specified javascript URLs.
    
    ``urls`` should be the exact URLs desired.  A previous version of this
    helper added magic prefixes; this is no longer the case.

    Specify the keyword argument ``defer=True`` to enable the script 
    defer attribute.
    """
    tags = []
    for url in urls:
        tag = HTML.tag("script", "", type="text/javascript", src=url, **attrs)
        tags.append(tag)
    return literal("\n").join(tags)


def stylesheet_link(*urls, **attrs):
    """Return CSS link tags for the specified stylesheet URLs.

    ``urls`` should be the exact URLs desired.  A previous version of this
    helper added magic prefixes; this is no longer the case.
    """
    if "href" in attrs:
        raise TypeError("keyword arg 'href' not allowed")
    attrs.setdefault("rel", "stylesheet")
    attrs.setdefault("type", "text/css")
    attrs.setdefault("media", "screen")
    tags = []
    for url in urls:
        tag = HTML.tag("link", href=url, **attrs)
        tags.append(tag)
    return literal('\n').join(tags)


def auto_discovery_link(url, feed_type="rss", **attrs):
    """Return a link tag allowing auto-detecting of RSS or ATOM feed.
    
    The auto-detection of feed for the current page is only for
    browsers and news readers that support it.

    ``url``
        The URL of the feed.  (This should be the exact URLs desired.  A
        previous version of this helper added magic prefixes; this is no longer
        the case.)

    ``feed_type``
        The type of feed. Specifying 'rss' or 'atom' automatically 
        translates to a type of 'application/rss+xml' or 
        'application/atom+xml', respectively. Otherwise the type is
        used as specified. Defaults to 'rss'.
    """
    if "href" in attrs:
        raise TypeError("keyword arg 'href' is not allowed")
    if "type" in attrs:
        raise TypeError("keyword arg 'type' is not allowed")
    title = ""
    if feed_type.lower() in ('rss', 'atom'):
        title = feed_type.upper()
        feed_type = 'application/{0}+xml'.format(feed_type.lower())
    attrs.setdefault("title", title)
    return HTML.tag("link", rel="alternate", type=feed_type, href=url, **attrs)


########## Lazy-rendering tags ##########

class Link(object):
    """A lazy-rendering hyperlink object.

    Attributes:

    * **label**: The text content. Can contain HTML markup or an image if you
      use a literal or the other helpers.
    * **url**: The URL target. Renders as the 'href' attribute.
    * **condition**: If true (default), render an <a> tag. If false, render
      only the text content.
    * **attrs**: Dict of HTML attributes.

    The 'condition' attribute is useful in cases like a menu where want the
    curent page to show just as text rather than a link.
    """

    def __init__(self, label, url="", condition=True, **attrs):
        """Constructor.
        
        The 'label' argument is required. If empty or ``None``, copy the URL to
        the label. The URL defaults to ``""``.
        """
        self.label = label or url
        self.url = url
        self.condition = condition
        self.attrs = attrs

    def __html__(self):
        if not self.condition:
            return HTML(self.label)
        return HTML.tag("a", self.label, href=self.url, **self.attrs)

    __str__ = __html__


########## Backward compatibility ##########

NL = HTML.NL
BR = HTML.BR


########## Private functions ##########

def _input(type, name, value, id, attrs):
    """Finish rendering an input tag."""
    attrs["type"] = type
    attrs["name"] = name
    attrs["value"] = value
    _set_id_attr(attrs, id, name)
    return HTML.tag("input", **attrs)

def _set_id_attr(attrs, id_arg, name):
    if "id_" in attrs:
        if id_arg is not NotGiven:
            raise TypeError("can't pass both 'id' and 'id_' args to helper")
        attrs["id"] = attrs.pop("id_")
    elif id_arg is NotGiven:
        attrs["id"] = _make_safe_id_component(name)
    elif id_arg is not None and id_arg != "":
        attrs["id"] = id_arg
    # Else id_arg is None or "", so do nothing.

def _make_safe_id_component(idstring):
    """Make a string safe for including in an id attribute.
    
    The HTML spec says that id attributes 'must begin with 
    a letter ([A-Za-z]) and may be followed by any number 
    of letters, digits ([0-9]), hyphens ("-"), underscores 
    ("_"), colons (":"), and periods (".")'. These regexps
    are slightly over-zealous, in that they remove colons
    and periods unnecessarily.
    
    Whitespace is transformed into underscores, and then
    anything which is not a hyphen or a character that 
    matches \w (alphanumerics and underscore) is removed.
    
    """
    # Transform all whitespace to underscore
    idstring = re.sub(r'\s', "_", '%s' % idstring)
    # Remove everything that is not a hyphen or a member of \w
    idstring = re.sub(r'(?!-)\W', "", idstring).lower()
    return idstring

def _repr(obj, *args):
    """Helper for ``.__repr__`` using attributes as positional args."""
    classname = obj.__class__.__name__
    args_str = ", ".join(repr(x) for x in args)
    return "{}({})".format(classname, args_str)
