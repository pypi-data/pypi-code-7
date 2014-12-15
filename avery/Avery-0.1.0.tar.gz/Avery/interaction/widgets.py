# Define some local widgets
#
import os
import fnmatch
from collections import OrderedDict
from IPython.html.widgets import (IntSliderWidget, ToggleButtonWidget,
                                  ContainerWidget, IntTextWidget,
                                  ButtonWidget, SelectWidget,
                                  TextWidget, HTMLWidget, DOMWidget)
from IPython.html.widgets.widget import CallbackDispatcher
from IPython.utils.traitlets import Int, Unicode
from IPython.utils.traitlets import link
from IPython.utils.py3compat import unicode_type

udown = unichr(0x25bc)
uleft = unichr(0x25c0)
def tb_description(value=False):
    if value:
        return udown
    else:
        return uleft

class IntTextSliderWidget(ContainerWidget):
    """
    Slider widget with optional text entry

    IntTextSliderWidget is a more flexible IntSliderWidget, modeled on
    the one in Mathematica Manipulate.  When created in the default
    closed state, it shows an ordinary slider widget, with a toggle
    button on the right.  Clicking the toggle button opens up a text
    widget that can be used to enter integers and increment and
    decrement buttons to change it by one. 

    Parameters
    ----------
    min, max: the range of the integer
    value: starting value
    description: Labels the slider widget. This description is also
        applied to the text widget and the Container.
    open: determines whether the text widget and buttons are visible
    """
    value = Int(sync=True)
    description = Unicode(sync=True)

    def __init__(
        self,
        min=1,
        max=100,
        value=1,
        description=u'',
        open=False
    ):
        self.sw = IntSliderWidget(min=min, max=max, value=value,
                                   description=description)
        self.tbw = ToggleButtonWidget(value=open,
                                      description=tb_description(open))
        self.topcw = ContainerWidget(children=[self.sw, self.tbw])
        self.tw = IntTextWidget(value=value, description=description)
        self.decb = ButtonWidget(description=u'<')
        self.incb = ButtonWidget(description=u'>')
        self.botcw = ContainerWidget(children=[self.tw, self.decb,
                                               self.incb])
        self.children = [self.topcw, self.botcw]
        self.value_link = link((self.sw, 'value'), (self.tw, 'value'),
                               (self, 'value'))
        self.open_link = link((self.tbw, 'value'),
                              (self.botcw, 'visible'))
        self.desc_link = link((self, 'description'),
                              (self.sw, 'description'))

        #
        # The following are instance-specific methods defined on
        # creation, since they need to know what widget to operate on,
        # and the widget doesn't identify itself to the callback.
        #
        def on_tbw_change(name, value):
            self.tbw.description = tb_description(value)
        self.tbw.on_trait_change(on_tbw_change, name='value')

        def on_decb_click(name):
            self.value -= 1
        self.decb.on_click(on_decb_click)

        def on_incb_click(name):
            self.value += 1
        self.incb.on_click(on_incb_click)

        def on_topcw_display(name):
            self.topcw.remove_class('vbox')
            self.topcw.add_class('hbox')
            self.topcw.set_css('width', '100%')
            self.topcw.add_class('center')
        self.topcw.on_displayed(on_topcw_display)
        on_topcw_display('')

        def on_botcw_display(name):
            self.botcw.remove_class('vbox')
            self.botcw.add_class('hbox')
            self.botcw.set_css('width', '100%')
            self.botcw.add_class('center')
        self.botcw.on_displayed(on_botcw_display)
        on_botcw_display('')

        #
        # It's not clear to me why this is necessary, but it is...
        #
        def on_display(name):
            on_topcw_display(name)
            on_botcw_display(name)
        self.on_displayed(on_display)
        on_display('')

class ClickSelectWidget(SelectWidget):
    """
    ClickSelectWidget extends SelectWidget to trigger a submit event
    when the user double-clicks a selection.
    """
    _view_name = Unicode('ClickSelectView', sync=True)

    # Code copied from the TextWidget of widget_string.py
    #
    def __init__(self, **kwargs):
        super(ClickSelectWidget, self).__init__(**kwargs)
        self._submission_callbacks = CallbackDispatcher()
        self.on_msg(self._handle_string_msg)

    def _handle_string_msg(self, _, content):
        """Handle a msg from the front-end.

        Parameters
        ----------
        content: dict
            Content of the msg."""
        if content.get('event', '') == 'submit':
            self._submission_callbacks(self)

    def on_submit(self, callback, remove=False):
        """(Un)Register a callback to handle choice submission.

        Triggered when the user clicks enter.

        Parameters
        ----------
        callback: callable
            Will be called with exactly one argument: the Widget instance
        remove: bool (optional)
            Whether to unregister the callback"""
        self._submission_callbacks.register_callback(callback, remove=remove)

class FileChoiceWidget(ContainerWidget):
    """
    A primitive file dialog widget.

    The widget contains four areas, a folder selection area, a file
    selection area, a filename text field, and a filter text
    field, in order from top to bottom. The two selection areas list
    directories (including '..', the parent directory) and plain
    files in the current directory. All directories are listed, but
    only those files matching the filter, a unix-style glob, are
    listed. To change directories, either double-click on a directory
    in the folders area, or type the name of a directory in the name
    field and hit enter. To select a file, double-click on a file in
    the files area or type the name of a file in the name field and
    hit enter. If you type a name that doesn't match either a
    directory or a filename, it is copied to the filter. You may also
    modify the filter directly. 

    The value of the widget is the absolute path to the file, once a
    file choice has been submitted. A callback can also be registered
    to respond to submission.

    The main public methods are __init__ and on_submit (to register a
    submission callback). Otherwise communication with the widget is
    mainly via its fields, especially value. 
    """
    description = Unicode(sync=True)
    value = Unicode(sync=True)
    filter = Unicode(sync=True)
    
    def __init__(
        self,
        dir=os.getcwdu(), 
        filter=u'*',
        description=u'',
        label=None,
        newFile=False
    ):
        """
        Create a new file choice widget.

        Parameters:
        -----------

        dir: The starting directory. Defaults to the current
            directory.
        filter=u'*': initial value of the filter. The default value *
            matches all filenames.
        description=u'': Widget description
        label=None: A label placed above the widget, if
            truthy. Defaults to the initial value of the description. 
        newFile=False: newFile False forces the choice of an existing
            file. 
        """
        super(FileChoiceWidget, self).__init__()
        self._submission_callbacks = CallbackDispatcher()
        self.dir = dir
        self.description = description
        if label == None:
            label = description
        self.label = label
        self.newFile = newFile
        self.fname = u''
        self.value = os.path.join(self.dir, self.fname)
        self.filter = filter
        self.findFiles(dir)
        htmlLabel = ('<p style=\"text-align:center\"><b>' + self.label
            + '</b></p>')
        self.labelWidget = HTMLWidget(value=htmlLabel,
                                      visible=True if self.label else False)
        self.dirWidget = ClickSelectWidget(values=self.dirs,
                                           description=u'folders')
        self.dirWidget.on_submit(self.onDirSubmit)
        self.plainWidget = ClickSelectWidget(values=self.plain,
                                             description=u'files')
        self.plainWidget.on_submit(self.onPlainSubmit)
        self.plainWidget.on_trait_change(self.onPlainChange)
        self.typeWidget = TextWidget(description='name')
        self.typeWidget.on_submit(self.onTypeSubmit)
        self.filterWidget = TextWidget(value=filter, description='filter')
        self.filterWidget.on_submit(self.onFilterSubmit)
        self.children = [self.labelWidget, self.dirWidget,
            self.plainWidget, self.typeWidget, self.filterWidget]

    def findFiles(self, dir=None):
        """
        Identify the directories and files matching the filter in the
        directory. Results are left in self.dirs and self.plain.

        Parameters:
        -----------
        dir: The directory to search. Defaults to self.dir.
        """
        dir = dir or self.dir
        files = os.listdir(dir)
        plain = []
        dirs = [os.pardir]
        for f in files:
            if os.path.isfile(os.path.join(dir, f)):
                plain.append(f)
            else:
                dirs.append(f)
        plain = fnmatch.filter(plain, self.filter)
        self.dirs = OrderedDict((unicode_type(f), f) for f in sorted(dirs))
        self.plain = OrderedDict((unicode_type(f), f) for f in sorted(plain))

    def path(self):
        """Return path corresponding to current dir and name"""
        fname = self.typeWidget.value
        path = os.path.join(self.dir, fname)
        path = os.path.abspath(path)
        return path

    def onDirSubmit(self, event):
        """
        Update choice widgets after new directory selection
        """
        dir = os.path.join(self.dir, self.dirWidget.value)
        dir = os.path.abspath(dir)
        if not os.path.isdir(dir):
            return  # ignore bad choices
        self.dir = dir
        self.findFiles()
        self.dirWidget.values = self.dirs
        self.plainWidget.values = self.plain
        
    def onPlainSubmit(self, event):
        """Fire submission event."""
        self.onTypeSubmit(event)

    def onPlainChange(self):
        """One-way sync from plain widget to type widget."""
        self.typeWidget.value = self.plainWidget.value

    def onTypeSubmit(self, event):
        """
        Main submission function. Test first whether the submitted
        value is a directory. If so, treat it as a directory
        submission. Otherwise, if it is a valid file choice (i.e.,
        either it exists, or newFile is True), fire the submission
        event. If both previous tests fail, make it the new filter.
        """
        if os.path.isdir(self.path()):
            self.dirWidget.value = self.typeWidget.value
            self.onDirSubmit(event)
        elif self.newFile or os.path.isfile(self.path()):
            self.fname = self.typeWidget.value
            try:
                self.plainWidget.value = self.typeWidget.value
            except KeyError:
                pass
            self.typeWidget.value = self.fname
            self.value = os.path.join(self.dir, self.fname)
            self._submission_callbacks(self)
        else:
            self.filterWidget.value = self.typeWidget.value
            self.onFilterSubmit(event)

    def onFilterSubmit(self, event):
        """
        Set the filter. If the new filter finds no matching files,
        append '*' to it.
        """
        self.filter = self.filterWidget.value
        self.findFiles()
        if not self.plain and (len(self.filter) == 0 or self.filter[-1] != '*'):
            self.filter += '*'
            self.filterWidget.value = self.filter
            self.findFiles()
        self.dirWidget.values = self.dirs
        self.plainWidget.values = self.plain

    def on_submit(self, callback, remove=False):
        """
        (Un)Register a callback to handle choice submission.

        Triggered when the user clicks enter.

        Parameters
        ----------
        callback: callable
            Will be called with exactly one argument: the Widget instance
        remove: bool (optional)
            Whether to unregister the callback
        """
        self._submission_callbacks.register_callback(callback,
                                                     remove=remove)

class AlertWidget(DOMWidget):
    """
    AlertWidget pops up an alert whenever value is changed, then
    clears value.
    """
    _view_name = Unicode('AlertWidgetView', sync=True)
    value = Unicode(sync=True)
