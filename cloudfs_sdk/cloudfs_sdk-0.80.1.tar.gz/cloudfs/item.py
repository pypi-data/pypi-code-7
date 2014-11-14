
from private.filesystem_common import move_items, copy_items
from private.utils import set_debug
from private.cloudfs_paths import VersionConflictValue, ExistValues, RestoreValue
from private.cached_object import CachedObject

from errors import operation_not_allowed, method_not_implemented
from path import Path

class Item(CachedObject):

    def __init__(self, rest_interface, data, parent_path=None, in_trash=False, share_key=None, old_version=False):
        super(Item, self).__init__(rest_interface, data)
        self.in_trash = in_trash
        self.share_key = share_key
        self.old_version = old_version
        self._create_from_json(data, parent_path)

    def _create_from_json(self, data, parent_path=None):
        if not parent_path:
            self._full_path = Path.path_from_string('/')
        elif isinstance(parent_path, Item):
            self._full_path = parent_path.path().copy()
        elif isinstance(parent_path, str):
            self._full_path = Path.path_from_string(parent_path)
        else:
            self._full_path = parent_path.copy()

        self._full_path.append(self.id)

    def _initialize_self(self, request_info, x_headers={}):
        if 'meta' in request_info:
            request_info = request_info['meta']
        self.data = request_info

    def in_share(self):
        return self.share_key != None

    # setters and getters
    @property
    def name(self):
        """
        :return: Name of item in filesystem.
        """
        return self._get('name')

    @name.setter
    def name(self, new_name):
        """ Set name of item.
        Note: if name is included when calling save() on an item, both extension and mime will be updated based
        on the new name of the item. This means that any modifications to mime will be ignored!
        :param new_name: New name for item.
        :return: Item
        """
        return self._set('name', new_name)

    @property
    def id(self):
        """
        :return: Id of item in filesystem. Used for paths.
        """
        return self._get('id')

    @id.setter
    def id(self, new_id):
        raise operation_not_allowed("Setting the id of an Item")

    @property
    def type(self):
        """
        :return: Type string of item in filesystem. Roughly corresponds to object type.
        """
        return self._get('type')

    @type.setter
    def type(self, new_type):
        raise operation_not_allowed("Setting the type of an Item")

    @property
    def is_mirrored(self):
        """
        Limited applications in CloudFS.
        :return: Boolean indicating if this item was created by mirroring a file on the users' desktop.
        """
        return self._get('is_mirrored')

    @is_mirrored.setter
    def is_mirrored(self, new_mirrored_flag):
        raise operation_not_allowed("Setting if an Item is mirrored")

    @property
    def date_content_last_modified(self):
        """
        :return: Timestamp for the last time the content of this item was modified. In seconds.
        """
        return self._get('date_content_last_modified', 0)

    @date_content_last_modified.setter
    def date_content_last_modified(self, new_date_content_last_modified):
        return self._set('date_content_last_modified', new_date_content_last_modified)

    @property
    def date_created(self):
        """
        :return: Timestamp this item was created. In seconds.
        """
        return self._get('date_created', 0)

    @date_created.setter
    def date_created(self, new_date_created):
        return self._set('date_created', new_date_created)

    @property
    def date_meta_last_modified(self):
        """
        :return: Timestamp for the last time the metadata was modified for this item. In Seconds.
        """
        return self._get('date_meta_last_modified', 0)

    @date_meta_last_modified.setter
    def date_meta_last_modified(self, new_date_meta_last_modified):
        return self._set('date_meta_last_modified', new_date_meta_last_modified)

    @property
    def application_data(self):
        """
        :return: Dictionary constructed from JSON. Contents are not defined in any way.
        """
        return self._get('application_data', {})

    @application_data.setter
    def application_data(self, new_application_data):
        raise method_not_implemented(self, 'set application_data')

    def url(self):
        return str(self._full_path)

    def path(self):
        return self._full_path

    def move_to(self, dest, exists=ExistValues.rename, debug=False):
        """Move item to destination.

        REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Move%20File.html
        REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Move%20Folder.html

        :param dest:        Path or Folder to move the items to.
        :param exists:      How to handle if an item of the same name exists in the destination folder. Defaults to rename.
        :param debug:       If true, will print the the request and response to stdout.

        :returns:   Details of the new item in a dictionary.
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.
        """
        move_items(self.rest_interface, [self], dest, exists, debug)

    def copy_to(self, dest, exists=ExistValues.rename, debug=False):
        """Copy item to destination.

        REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Copy%20File.html
        REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Copy%20Folder.html

        :param dest:        Path or Folder to copy the items to.
        :param exists:      How to handle if an item of the same name exists in the destination folder. Defaults to rename.
        :param debug:       If true, will print the the request and response to stdout.

        :returns:   Details of the new item in a dictionary.
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.
        """
        copy_items(self.rest_interface, [self], dest, exists, debug)


    def delete(self, commit=False, debug=False):
        raise Exception('Delete not implemented for item base class!')

    def save(self, if_conflict=VersionConflictValue.fail, debug=False):
        raise Exception('Save not implemented for item base class!')

    def restore(self, restore_method=RestoreValue.fail, method_argument=None, debug=False):
        """Restore item from trash.
        REST documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Recover%20Trash%20Item.html
        :param dest:
        :return:
        """
        if self.in_share():
            raise operation_not_allowed("restore item in share")
        if not self.in_trash:
            # TODO: Should we filter on this? It should be reliable - but we can't guarentee it.
            return None

        set_debug(self, debug)
        return self.rest_interface.restore_trash_item(self.path(), restore_method, method_argument)

    def __eq__(self, other):
        if hasattr(other, 'data') and 'id' in getattr(other, 'data'):

            return self.data['id'] == getattr(other, 'data')['id']
        return False

    def __str__(self):
        return 'Item:{}'.format(self.id)

    def __repr__(self):
        return self.__str__()