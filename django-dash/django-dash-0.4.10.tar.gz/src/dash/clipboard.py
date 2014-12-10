__all__ = (
    'save_plugin_data_to_clipboard', 'get_plugin_data_from_clipboard',
    'cut_entry_to_clipboard', 'copy_entry_to_clipboard',
    'paste_from_clipboard', 'can_paste_from_clipboard'
)

from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _

from dash.models import (
    DashboardEntry, DashboardWorkspace
    )
from dash.settings import PLUGIN_CLIPBOARD_KEY
#from dash.helpers import validate_placeholder
#from dash.placeholder_utils import get_available_placeholder_space, get_available_template_placeholder_space

# *********************************************
# *********************************************
# ******* Clipboard of dasbhoard entries ******
# *********************************************
# *********************************************

def save_plugin_data_to_clipboard(request, plugin_uid, plugin_data):
    """
    Saves plugin to clipboard for later pasting.

    :param django.http.HttpRequest request:
    :param str plugin_uid:
    :param str plugin_data: JSON data (stringified).
    :return bool: True on success. False otherwise.
    """
    request.session[PLUGIN_CLIPBOARD_KEY] = {
        'plugin_uid': plugin_uid,
        'plugin_data': plugin_data
    }
    return True

def get_plugin_data_from_clipboard(request):
    """
    Retrieves the plugin clipboard (note, that only last element is being saved).

    :param django.http.HttpRequest:
    :return dict:
    """
    if PLUGIN_CLIPBOARD_KEY in request.session:
        return request.session[PLUGIN_CLIPBOARD_KEY]

def clear_clipboard_data(request):
    """
    Clear the clipboard data.
    """
    if PLUGIN_CLIPBOARD_KEY in request.session:
        request.session[PLUGIN_CLIPBOARD_KEY] = None

def cut_entry_to_clipboard(request, dashboard_entry, \
                           delete_original_entry=True, \
                           clone_plugin_data=True):
    """
    Cut ``dash.models.DashboardEntry`` to clipboard.

    :param django.http.HttpRequest request:
    :param dash.models.DashboardEntry dashboard_entry:
    :param bool delete_original_entry: If set to True, original entry is deleted; kept otherwise.
    :return bool: True on success. False otherwise.
    """
    plugin_uid = dashboard_entry.plugin_uid

    if clone_plugin_data:
        plugin = dashboard_entry.get_plugin(request=request)

        # Getting cloned plugin data
        plugin_data = plugin._clone_plugin_data(dashboard_entry)

        # If none returned, using the still the current one (not cloned, which is dangerous). Possible TODO
        # for later.
        if plugin_data is None:
            plugin_data = dashboard_entry.plugin_data
    else:
        plugin_data = dashboard_entry.plugin_data

    save_plugin_data_to_clipboard(
        request = request,
        plugin_uid = plugin_uid,
        plugin_data = plugin_data
        )

    if delete_original_entry:
        dashboard_entry.delete()

    return True

def copy_entry_to_clipboard(request, dashboard_entry):
    """
    Copy ``dash.models.DashboardEntry`` to clipboard.

    :param django.http.HttpRequest request:
    :param dash.models.DashboardEntry dashboard_entry:
    :return bool: True on success. False otherwise.
    """
    return cut_entry_to_clipboard(
        request, dashboard_entry, delete_original_entry=False
        )

def paste_from_clipboard(request, layout_uid, placeholder_uid, workspace=None, \
                         entries=[], check_only=False, clear_clipboard=True):
    """
    Pastes entry from clipboard to the given placeholder of a workspace selected.

    :param django.http.HttpRequest request:
    :param str placeholder: Placeholder UID.
    :param mixed workspace: Either str or ``dash.models.DashboardWorkspace``
        instance. If str is given, a database hit occurs in order to obtain
        the ``dash.models.DashboardWorkspace`` instance. Thus, if you have the
        workspace instance already, provide it as is, in order to minify
        database hits.
    :param iterable entries: If given, entries are not fetched but the
        existing iterable is used. Each item in the iterable should be an
        instance of ``dash.models.DashboardEntry``.
    :param bool check_only: If set to True, it's only checked if it's possible
        to paste from clipboard (the ``dashboard_entry.save()`` part is
        skipped, which means that the entry is not saved in the database).
    :return tuple (str, bool): (Plugin name, boolean True) tuple on success
        and (error message, boolean False) on failure.
    """
    clipboard_plugin_data = get_plugin_data_from_clipboard(request)
    if not clipboard_plugin_data: #or not 'plugin_name' in request.session[PLUGIN_CLIPBOARD_KEY]
        return (_("Clipboard is empty!"), False)

    # TODO
    #if not validate_placeholder(placeholder):
    #    return (_("Invalid placeholder ``{0}``!").format(placeholder), False)

    if isinstance(workspace, DashboardWorkspace):
        workspace_obj = workspace
    else:
        if workspace:
            try:
                workspace_obj = DashboardWorkspace._default_manager.get(slug=workspace)
            except ObjectDoesNotExist as e:
                workspace_obj = None
        else:
            workspace_obj = None

    dashboard_entry = DashboardEntry(
        user = request.user,
        workspace = workspace_obj,
        layout_uid = '', # TODO
        placeholder_uid = placeholder_uid,
        plugin_uid = clipboard_plugin_data['plugin_uid'],
        plugin_data = clipboard_plugin_data['plugin_data'],
        undeletable = False
    )

    # We should now check if we have a space for pasting the plugin. For that we should get the plugin and
    # see if there's a space available for the (workspace, placeholder, user) triple given.

    # Get the plugin.
    plugin = dashboard_entry.get_plugin()

    # Calculate available space.
    available_placeholder_space = get_available_placeholder_space(
        placeholder_uid = placeholder,
        user = request.user,
        workspace_slug = workspace_obj.slug if workspace_obj and workspace_obj.slug else None,
        entries = entries
        )

    # Calculate how much space the to be pasted plugin occupies.
    plugin_cols, plugin_rows = plugin.get_dimensions()

    # See if it's enough for it to be pasted. If not, return False; otherwise, continue and save the
    # dashboard entry.
    if (plugin_cols * plugin_rows) > available_placeholder_space:
        return (_("Space occupied by function to be pasted exceeds the available placeholder space!"), False)
    try:
        if not check_only:
            # Save data
            dashboard_entry.save()

            # Clear the clipboard
            clear_clipboard_data(request)

        return (clipboard_plugin_data['plugin_name'], True)
    except Exception as e:
        return (str(e), False)

def can_paste_from_clipboard(request, placeholder, workspace=None, entries=[]):
    """
    Check if clipboard plugin can be pasted into the placeholder. For actually pasting the plugin from clipboard
    into the placeholder, use ``dash.clipboard.paste_from_clipboard`` function.

    :param django.http.HttpRequest request:
    :param str placeholder: Placeholder UID.
    :param mixed workspace: Either str or ``dash.models.DashboardWorkspace`` instance. If str is given, a database
        hit occurs in order to obtain the ``dash.models.DashboardWorkspace`` instance. Thus, if you have the
        workspace instance already, provide it as is, in order to minify database hits.
    :param iterable entries: If given, entries are not fetched but the existing iterable is used. Each item in
        the iterable should be an instance of ``dash.models.DashboardEntry``.
    :return tuple (str, bool): (Plugin name, boolean True) tuple on success and (error message, boolean False)
        on failure.
    """
    return paste_from_clipboard(
        request = request,
        placeholder = placeholder,
        workspace = workspace,
        entries = entries,
        check_only = True
        )

# ***********************************************
# ***********************************************
# *** Clipboard of Dasbhoard template entries ***
# ***********************************************
# ***********************************************

def save_template_entry_data_to_clipboard(request, plugin_uid, plugin_data):
    """
    Saves plugin to clipboard for later pasting.

    :param django.http.HttpRequest request:
    :param str plugin_uid:
    :param str plugin_data: JSON data (stringified).
    :return bool: True on success. False otherwise.
    """
    request.session[DASHBOARD_TEMPLATE_CLIPBOARD_KEY] = {
        'plugin_uid': plugin_uid,
        'plugin_data': plugin_data
    }
    return True

def get_template_entry_data_from_clipboard(request):
    """
    Retrieves the plugin clipboard (note, that only last element is being saved).

    :param django.http.HttpRequest:
    :return dict:
    """
    if DASHBOARD_TEMPLATE_CLIPBOARD_KEY in request.session:
        return request.session[DASHBOARD_TEMPLATE_CLIPBOARD_KEY]

def clear_template_clipboard_data(request):
    """
    Clear the dashboard template GUI clipboard data.
    """
    if DASHBOARD_TEMPLATE_CLIPBOARD_KEY in request.session:
        request.session[DASHBOARD_TEMPLATE_CLIPBOARD_KEY] = None

def cut_template_entry_to_clipboard(request, dashboard_template_entry, delete_original_entry=True, \
                                    clone_plugin_data=True):
    """
    Saves ``dash.models.DashboardEntry`` to clipboard.

    :param django.http.HttpRequest request:
    :param dash.models.DashboardTemplateEntry dashboard_entry:
    :param bool delete_original_entry: If set to True, original entry is deleted; kept otherwise.
    :return bool: True on success. False otherwise.
    """
    plugin_uid = dashboard_template_entry.plugin_uid

    if clone_plugin_data:
        plugin = dashboard_template_entry.get_plugin()

        # Getting cloned plugin data
        plugin_data = plugin._clone_plugin_data(dashboard_template_entry)

        # If none returned, using the still the current one (not cloned, which is dangerous). Possible TODO
        # for later.
        if plugin_data is None:
            plugin_data = dashboard_template_entry.plugin_data
    else:
        plugin_data = dashboard_template_entry.plugin_data

    save_template_entry_data_to_clipboard(request=request, plugin_uid=plugin_uid, plugin_data=plugin_data)

    if delete_original_entry:
        dashboard_template_entry.delete()

    return True

def copy_template_entry_to_clipboard(request, dashboard_template_entry):
    """
    Copy ``dash.models.DashboardEntry`` to clipboard.

    :param django.http.HttpRequest request:
    :param dash.models.DashboardTemplateEntry dashboard_template_entry:
    :return bool: True on success. False otherwise.
    """
    return cut_template_entry_to_clipboard(request, dashboard_template_entry, delete_original_entry=False)

def paste_template_entry_from_clipboard(request, placeholder, template=None, entries=[], check_only=False, \
                                        clear_clipboard=True):
    """
    Pastes entry from clipboard to the given placeholder of a workspace selected.

    :param django.http.HttpRequest request:
    :param str placeholder: Placeholder UID.
    :param mixed workspace: Either str or ``dash.models.DashboardWorkspace`` instance. If str is given, a database
        hit occurs in order to obtain the ``dash.models.DashboardWorkspace`` instance. Thus, if you have the
        workspace instance already, provide it as is, in order to minify database hits.
    :param iterable entries: If given, entries are not fetched but the existing iterable is used. Each item in
        the iterable should be an instance of ``dash.models.DashboardEntry``.
    :param bool check_only: If set to True, it's only checked if it's possible to paste from clipboard (the
        ``dashboard_entry.save()`` part is skipped, which means that the entry is not saved in the database).
    :return tuple (str, bool): (Plugin name, boolean True) tuple on success and (error message, boolean False)
        on failure.
    """
    clipboard_plugin_data = get_template_entry_data_from_clipboard(request)
    if not clipboard_plugin_data: #or not 'plugin_name' in request.session[PLUGIN_CLIPBOARD_KEY]
        return (_("Clipboard is empty!"), False)

    if not validate_placeholder(placeholder):
        return (_("Invalid placeholder ``{0}``!").format(placeholder), False)

    if isinstance(template, DashboardTemplate):
        template_obj = template
    else:
        if template:
            try:
                template_obj = DashboardTemplate._default_manager.get(pk=template)
            except ObjectDoesNotExist as e:
                template_obj = None
        else:
            template_obj = None

    dashboard_template_entry = DashboardTemplateEntry(
        template = template_obj,
        placeholder = placeholder,
        plugin_uid = clipboard_plugin_data['plugin_uid'],
        plugin_data = clipboard_plugin_data['plugin_data'],
        undeletable = False
    )

    # We should now check if we have a space for pasting the plugin. For that we should get the plugin and
    # see if there's a space available for the (workspace, placeholder, user) triple given.

    # Get the plugin.
    plugin = dashboard_template_entry.get_plugin()

    # Calculate available space.
    available_placeholder_space = get_available_template_placeholder_space(
        placeholder_uid = placeholder,
        template_id = template_obj.pk if template_obj and template_obj.pk else None,
        entries = entries
        )

    # Calculate how much space the to be pasted plugin occupies.
    plugin_cols, plugin_rows = plugin.get_dimensions()

    # See if it's enough for it to be pasted. If not, return False; otherwise, continue and save the
    # dashboard entry.
    if (plugin_cols * plugin_rows) > available_placeholder_space:
        return (_("Space occupied by function to be pasted exceeds the available placeholder space!"), False)
    try:
        if not check_only:
            # Save data
            dashboard_template_entry.save()

            # Clear the clipboard
            clear_template_clipboard_data(request)

        return (clipboard_plugin_data['plugin_name'], True)
    except Exception as e:
        return (str(e), False)

def can_paste_template_entry_from_clipboard(request, placeholder, template=None, entries=[]):
    """
    Check if clipboard plugin can be pasted into the placeholder. For actually pasting the plugin from clipboard
    into the placeholder, use ``dash.clipboard.paste_from_clipboard`` function.

    :param django.http.HttpRequest request:
    :param str placeholder: Placeholder UID.
    :param mixed template: Either str or ``dash.models.DashboardTemplate`` instance. If str is given, a database
        hit occurs in order to obtain the ``dash.models.DashboardTemplate`` instance. Thus, if you have the
        template instance already, provide it as is, in order to minify database hits.
    :param iterable entries: If given, entries are not fetched but the existing iterable is used. Each item in
        the iterable should be an instance of ``dash.models.DashboardEntry``.
    :return tuple (str, bool): (Plugin name, boolean True) tuple on success and (error message, boolean False)
        on failure.
    """
    return paste_template_entry_from_clipboard(
        request = request,
        placeholder = placeholder,
        template = template,
        entries = entries,
        check_only = True
        )
