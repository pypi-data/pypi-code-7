import StringIO
from os.path import exists, isdir, split, join

from private.filesystem_common import create_items_from_json
from private.cloudfs_paths import VersionConflictValue
from private.utils import set_debug

from item import Item
from errors import method_not_implemented, operation_not_allowed, invalid_argument


class File(Item):
    def __init__(self, rest_interface, data, parent_path=None, in_trash=False, share_key=None, old_version=False):
        super(File, self).__init__(rest_interface, data, parent_path, in_trash, share_key, old_version)
        self.offset = 0

    def _refresh_request(self, debug=False):
        set_debug(self, debug)
        return self.rest_interface.file_get_meta(self.path())

    def _prevent_unsupported_operation(self, method):
        messages = {
            'delete':{
                'share':   'delete file in share',
                'previous':'delete previous version of file'
            },
            'save':{
                'share':   'save file in share',
                'previous':'save changes to previous version of file'
            },
            'versions':{
                'share':   'list file versions in share'
            },
            'download':{
                'share':   'download file in share',
                'previous':'download previous version of file'
            },
            'read':{
                'share':   'read file in share',
                'previous':'read previous version of file'
            },
            'seek':{
                'share':   'seek in file in share',
                'previous':'seek in previous version of file'
            }
        }
        try:
            state_messages = messages[method]
        except KeyError:
            print "Failed to check that operation '{}' is allowed due to missing messages!".format(method)
            # do noting! D:
            return

        if self.in_share() and 'share' in state_messages:
            raise operation_not_allowed(state_messages['share'])
        if self.old_version and 'previous' in state_messages:
            raise operation_not_allowed(state_messages['previous'])


    @staticmethod
    def _get_download_callback(fp, close=True):
        # preserve env
        def callback(response):
            for chunk in response.iter_content(chunk_size=128):
                if chunk:
                    fp.write(chunk)
                    fp.flush()
            fp.seek(0)
            if close:
                fp.close()

        return callback

    def delete(self, commit=False, debug=False):
        """Delete the file.

        REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Delete%20File.html

        :param commit:  If true, will permanently remove the file. Will move to trash otherwise. Defaults to False.
        :param debug:   If true, will print the the request and response to stdout.

        :returns:   Dictionary with keys for success and the deleted files last version.
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.
        """
        if self.in_trash:
            if commit:
                set_debug(self, debug)
                return self.rest_interface.delete_trash_item(self.path())
            else:
                # nop
                # we're already in the trash, does not make sense to make a delete call if commit is not true.
                return {}

        self._prevent_unsupported_operation('delete')

        set_debug(self, debug)
        result = self.rest_interface.delete_file(self.path(), commit)
        if result['success'] and commit == False:
            self.in_trash = True
        return result

    def promote(self, debug=False):
        """Promote this version of the file and replace the current version.

        This function will throw an exception if called on a file that is not a previous version.
        Updates this file object to the promoted & current file.

        :return:                        Updated version of file.
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.
        """
        if not self.old_version:
            raise operation_not_allowed('promote the current version of the file')
        set_debug(self, debug)

        version = self._get('version', None)
        if not version:
            raise ValueError('{} did not have a version field in its data dictionary!:{} \nDid we have a massive & breaking API change?'.format(str(self), self.data))

        response = self.rest_interface.promote_file_version(self.path(), version)
        self._initialize_self(response)
        self.old_version = False
        return self



    def save(self, if_conflict=VersionConflictValue.fail, debug=False):
        """Save changes to the file.
        See notes on individual setters for quirks.

        REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Alter%20File%20Meta.html

        :param if_conflict:    Behavior if the file has been updated since retrieving it from Cloudfs.
        :param debug:          If true, will print the the request and response to stdout.

        :returns:  Updated file object
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.
        """
        self._prevent_unsupported_operation('save')
        set_debug(self, debug)
        changes = {'version':self.data['version']}
        for changed_key in self.changed_meta:
            changes[changed_key] = self.data[changed_key]

        self.changed_meta.clear()
        response =  self.rest_interface.file_alter_meta(self.path(), changes, if_conflict)
        self._initialize_self(response)
        return self

    def versions(self, start=0, end=None, limit=10, debug=False):
        """List the previous versions of this file

        The list of files returned are mostly non-functional, though their meta-data is correct. They cannot be read /
        moved / copied, etc.

        :param start:   Lowest version number to list. Optional, defaults to listing all file versions.
        :param stop:    Last version of the file to list. Optional, defaults to listing the most recent version of the file.
        :param limit:   Limit on number of versions returned. Optional, defaults to 10.
        :return:        List of previous versions of this file.
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.
        """

        self._prevent_unsupported_operation('versions')
        set_debug(self, debug)
        results = self.rest_interface.list_file_versions(self.path(), start, end, limit)
        if len(results) > 0:
            results = create_items_from_json(self.rest_interface, results, self.path()[:-1], old_versions=True)
        return results

    def wait_for_downloads(self, timeout=None):
        """ Wait for any threaded downloads started by this file.
        Warning: By default, this will be called without a timeout on deletion, preventing
        program close for some time. This can be avoided by calling this at least once with
        any timeout.

        :param timeout: Floating point number of seconds to wait. If none, waits indefinitely. Optional.
        :return: True if all downloads are complete. False otherwise.
        """
        return self.rest_interface.wait_for_downloads(timeout)

    def download(self, local_path, custom_name=None, synchronous=False, debug=False):
        """Download the file to the local filesystem.
        Does not replicate any metadata.
        If downloads are started with synchronous=True CloudFS SDK will attempt to block until all downloads are complete on destruction. This may block your
        program from exiting. To avoid this, call wait_for_downloads at least once with any arguments (i.e. call with a timeout of 0 to halt downloads immediately)

        REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Download%20File.html

        :param local_path:  Path on local filesystem. Can end with a file name, which will be created or overwritten. Will not create any folders.
        :param custom_name: Can use a separate argument to specify local file name. If file name is included in both local_path and this, local_path takes priority. Optional.
        :param synchronous: If true, download will return immediately and download in separate thread.
        :param debug:       If true, will print the the request and response to stdout.
        :return: None
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.
        :raises InvalidArgument:        Based on CloudFS Error Code.
        """
        self._prevent_unsupported_operation('download')
        set_debug(self, debug)

        file_name = custom_name
        local_path_except = invalid_argument('local_path', 'Full path of a folder or file that exists. Alternatively, a non-existent file in an existing hierarchy of folders', local_path)

        if exists(local_path):
            if isdir(local_path):
                # use our name / custom name in directory
                folder_path = local_path
            else:
                # use whole users' path
                folder_path, file_name = split(local_path)
                if not file_name:
                    raise local_path_except
        else:
            folders, file = split(local_path)
            if exists(folders):
                file_name = file
                folder_path = folders
            else:
                raise local_path_except

        if not file_name:
            file_name = self.name


        full_path = join(folder_path, file_name)
        fp = open(full_path, 'wb')

        self.rest_interface.download(self.path(), self._get_download_callback(fp, True), background=(not synchronous))

    # file interface
    def read(self, size=None, debug=False):
        """File-like interface to read file. Reads size bytes from last offset.
        Reads file synchronously - does not start threads.
        Warning: Each read() call generates on request to CloudFS.

        REST Documentation: https://www.bitcasa.com/cloudfs-api-docs/api/Download%20File.html

        :param size:    Number of bytes to read. If None, will read entire file. Defaults to None.
        :param debug:   If true, will print the the request and response to stdout.
        :return:    File contents.
        """
        self._prevent_unsupported_operation('read')
        set_debug(self, debug)
        range = None
        fp = StringIO.StringIO()
        if size:
            range = [self.tell(), self.tell() + size - 1]
            self.offset += size

        self.rest_interface.download(self.path(), self._get_download_callback(fp, False), range=range)

        return fp.read()

    def readline(self, size=None):
        raise method_not_implemented(self, 'readline')

    def readlines(self, sizehint=None):
        raise method_not_implemented(self, 'readlines')

    def seek(self, offset, whence=0):
        """Seek to the given offset in the file.

        :param offset:  Number of bytes to seek.
        :param whence:  Seek be
        :return:        resulting offset
        """
        self._prevent_unsupported_operation('seek')
        if whence == 0:
            self.offset = offset
        if whence == 1:
            self.offset += offset
        if whence == 2:
            self.offset = self.data['length'] - offset

        if offset > self.size:
            offset = self.size
        if offset < 0:
            offset = 0

        return offset

    def tell(self):
        """
        :return: Current offset of file-like interface.
        """
        return self.offset

    def truncate(self, size=0):
        raise method_not_implemented(self, 'truncate')

    # Soon
    def write(self):
        raise method_not_implemented(self, 'write')

    def writelines(self):
        raise method_not_implemented(self, 'writelines')

    @property
    def extension(self):
        """
        :return: Extension of file.
        """
        return self._get('extension')

    @extension.setter
    def extension(self, new_extension):
        raise operation_not_allowed("Setting extension directly instead of name")

    @property
    def mime(self):
        """
        :return: Mime type of file.
        """
        return self._get('mime')

    @mime.setter
    def mime(self, new_mime):
        return self._set('mime', new_mime)

    @property
    def size(self):
        return self._get('size')

    @size.setter
    def size(self, new_size):
         raise operation_not_allowed("Setting the size of an Item")

    def __str__(self):
        tags = '{}{}{}'.format(
            'T' if self.in_trash else '_',
            'S' if self.share_key else '_',
            'O' if self.old_version else '_',
        )
        return "{}({})[File|{}]:{} {} bytes".format(self.name.encode('utf-8'), self.mime.encode('utf-8'), tags, self.id, self.size)
