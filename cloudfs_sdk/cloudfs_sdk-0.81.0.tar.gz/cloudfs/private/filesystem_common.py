import collections

from ..errors import invalid_argument, CloudFSError, operation_not_allowed
from utils import set_debug

def list_items_from_path(rest_interface, path, in_trash=False):
    if in_trash:
        response = rest_interface.list_trash(path)
    else:
        response = rest_interface.list_folder(path)
    path = path if str(path) != '/' else None

    # only use actual response
    return create_items_from_json(rest_interface, response, path, in_trash)

def _set_debug_operation(rest_interface, debug):
        fake_object = {'rest_interface':rest_interface}
        # the twists we go through to centralize control
        def call_set_debug():
            set_debug(fake_object, debug)

        return call_set_debug

def move_items(rest_interface, items, destination, exists, debug):
    from ..file import File
    from ..container import Folder
    from ..item import Item
    if isinstance(destination, Item):
        destination = destination.path()

    operations = {
        File:lambda file: rest_interface.move_file(file.path(), destination, file.name, exists),
        Folder:lambda file: rest_interface.move_folder(file.path(), destination, file.name, exists)
    }

    return _process_items_by_type(items, operations, _set_debug_operation(rest_interface, debug))

def copy_items(rest_interface, items, destination, exists, debug):
    from ..file import File
    from ..container import Folder
    from ..item import Item
    if isinstance(destination, Item):
        destination = destination.path()

    operations = {
        File:lambda file: rest_interface.copy_file(file.path(), destination, file.name, exists),
        Folder:lambda file: rest_interface.copy_folder(file.path(), destination, file.name, exists)
    }

    return _process_items_by_type(items, operations, _set_debug_operation(rest_interface, debug))

def _process_items_by_type(items, operation_dictionary, debug):
    from ..item import Item
    if type(items) is not list and type(items) is not tuple:
        items = [items]
    for item in items:
        if isinstance(item, Item) and item.in_share():
            raise operation_not_allowed("Cannot execute this operation on items in a share.")
        if type(item) in operation_dictionary:
            # set debug if needed
            debug()
            op = operation_dictionary[type(item)]
            op(item)
        else:
            raise invalid_argument(
                'item in list',
                '{}'.format([operation_dictionary.keys()]),
                str(type(item)))


def create_items_from_json(rest_interface, data, parent_path, in_trash=False, share_key=None, old_versions=False):
    from ..file import File
    from ..container import Folder
    from ..share import Share
    if 'results' in data:
        data = data['results']

    if 'items' in data:
        data = data['items']

    items = []

    parent_item = None # root
    if parent_path and str(parent_path) != '/':

        if not parent_item:
            parent_item = parent_path

    def create_item(item_json, parent):
        new_item = None
        if 'type' not in item_json and 'share_key' in item_json:
            new_item = Share(rest_interface.get_copy(), item_json)
        elif item_json['type'] == 'folder':
            new_item = Folder(rest_interface.get_copy(), item_json, parent, in_trash, share_key)
        elif item_json['type'] == 'file':
            new_item = File(rest_interface.get_copy(), item_json, parent, in_trash, share_key, old_versions)
        elif item_json['type'] == 'root': #lolololololol
            # sometimes you can end up having a root object added to your root.
            # Yo Dawg
            return
        else:
            raise CloudFSError('Did not recognize item from JSON: {}'.format(item_json))

        items.append(new_item)


    # single item from upload / etc
    if isinstance(data, collections.Mapping):
        create_item(data, parent_item)
    else:
        # directory listing
        for item in data:
            create_item(item, parent_item)


    return items
