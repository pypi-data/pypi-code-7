import os, datetime, re
from tzlocal import get_localzone
from collections import OrderedDict

from .configuration import Configuration
from .change_db import ChangeDB, GDriveFile, GDriveDirectory
from . import gdrive_communication as api

class GDriveSyncError(Exception):
    pass

SYSTEM_TZ = get_localzone()

class GDriveSyncDifference(object):
    ONLY_LOCAL = 'only_local'
    ONLY_REMOTE = 'only_remote'
    NEWER_LOCAL = 'newer_local'
    FILES_ARE_DIFFERENT = 'files_differ'
    FILE_DIRECTORY_MISMATCH = 'type_mismatch'

    def __init__(self, reason, remote_item=None, local_item=None):
        self.reason = reason
        self.remote_item = remote_item
        self.local_item = local_item

    def __str__(self):
        return "GDriveSyncDiff, Reason: %s, Local: %s, Remote: %s" % (self.reason, self.local_item, self.remote_item)
      
class LocalItem(object):
    def __init__(self, path):
        assert os.path.exists(path)
        self.path = path
        self._modified = None
        self._file_size = None
        self._is_file = None

    def __str__(self):
        return self.path

    @property
    def is_file(self):
        if self._is_file is None:
            self._is_file = os.path.isfile(self.path)
        return self._is_file

    @property
    def is_dir(self):
        return not self.is_file

    @property
    def modified(self):
        if self._modified is None:
            t = os.path.getmtime(self.path)
            self._modified = datetime.datetime.fromtimestamp(t, SYSTEM_TZ)
        return self._modified
    
    @property
    def file_size(self):
        if self._file_size is None:
            self._file_size = os.path.getsize(self.path)
        return self._file_size
  
class GDriveSync():
    def __init__(self, configuration_directory=None, verbose=False):
        self.config = Configuration(configuration_directory)
        self.change_db = ChangeDB(self.config.changes_file, logger=self.log)
        self.verbose = verbose
        self.root = None
        self.drive = None
        api.log = self.log
        self.logged_warnings = []
        self.logged_errors = []
        
    def connect(self):
        """
        Connect and authenticate with the Google Drive web service 
        """
        if self.drive is None:
            self.drive = api.connect(credentials_file=self.config.credentials_file)

    def is_connected(self):
        return self.drive is not None

    def update(self):
        """
        Update the local change database with any changes made to the Drive since last update
        """
        api.update(self.drive, self.change_db)
        
    def build_file_tree(self, root_id=None):
        """
        Build the google Drive file tree from the change list
        """
        if root_id is None:
            if not self.is_connected():
                self.connect()

            root_id = api.get_drive_root_id(self.drive)

        self.root = self.change_db.get_file_tree(root_id=root_id)
        
    def add_item(self, diff, local_base_dir, remote_base_dir, dry_run=False):
        """
        Add a file to google drive
        """
        # Get name on drive
        rel_path = os.path.relpath(os.path.abspath(diff.local_item.path),
                                   os.path.abspath(local_base_dir))
        rel_path = rel_path.replace(os.pathsep, '/')
        if rel_path == '.':
            drive_path = remote_base_dir
        else:
            drive_path = remote_base_dir + '/' + rel_path

        print drive_path

        drive_dir = os.path.split(drive_path)[0]
        print 'looking for', drive_dir
        try:
            parent = self.root.get_child(drive_dir)
        except KeyError:
            if dry_run:
                # Can't find the directory, if it's parent would also be created in this run.
                self.log('Would create %s in %s' % (drive_path, drive_dir))
                return
            else:
                raise Exception("Unknown behaviour")

        print 'parent is', parent.__str__()

        self.log('Creating  %s in %s' % (drive_path, drive_dir))
        if dry_run:
            return

        try:
            info = api.upload(self.drive, diff, parent.id)
        except api.errors.HttpError as e:
            self.log('Cannot add item %s' % diff.local_item, 'warning')
            self.log(e.message)
            return
        if diff.local_item.is_file:
            newitem = GDriveFile(info, parents=[parent])
        else:
            newitem = GDriveDirectory(info, parents=[parent])
        parent.add_child(newitem)

        #print info

    def update_item(self, diff, dry_run=False):
        """
        Upload a file (optionally update file that is already there)
        """

        assert diff.local_item.is_file

        self.log('Updating file %s from %s' % (diff.remote_item, diff.local_item))
        if dry_run:
            return

        try:
            _info = api.upload(self.drive, diff)
        except api.errors.HttpError as e:
            self.log('Cannot update file %s' % diff.local_item, 'warning')
            self.log(e.message)

    def delete_item(self, diff, remote_file_path, keep_multiple=False, dry_run=False):
        """
        Delete a file (move to trash)
        """
        # Get hold of 
        item = diff.remote_item
        if keep_multiple and len(item.parents) > 1:
            to_remove_parents = []
            for parent in item.parents:
                for path in parent.path:
                    if path.startswith('/' + remote_file_path):
                        to_remove_parents.append(parent)
            
            # remove duplicates
            to_remove_parents = list(OrderedDict.fromkeys(to_remove_parents))
            assert len(to_remove_parents) == 1
            to_remove_parent = to_remove_parents[0]
            try:
                api.delete(self.drive, diff, parent=to_remove_parent.id)
                to_remove_parent.unlink_child(item)
            except api.errors.HttpError as e:
                self.log('Cannot delete %s' % item, 'warning')
                self.log(str(e))
                return


        self.log('Deleting file %s' % item)
        
        if dry_run:
            return
        
        try:
            _info = api.delete(self.drive, diff)
        except api.errors.HttpError as e:
            self.log('Cannot delete %s' % item, 'warning')
            self.log(str(e))
            return
        
        for p in item.parents:
            p.unlink_child(item)

    def walk_drive(self, drive_dir):
        drive_dir_obj = self.root.get_child(drive_dir)

        if not drive_dir_obj.is_dir:
            raise GDriveSyncError('Requested path %r is not a directory on the Drive' % drive_dir)

        stack = [(child, [child.name]) for child in drive_dir_obj.children.itervalues()]
        while stack:
            item, pth = stack.pop()
            yield (item, pth)
            if item.is_dir:
                stack.extend((child, pth + [child.name]) for child in item.children.itervalues())

    def walk_syncable(self, drive_dir):
        for item, pth in self.walk_drive(drive_dir):
            dpath = [path for path in item.path if path.startswith('/' + drive_dir)]

            if len(dpath) == 1:
                # Only one path, fine!
                yield item, pth
            else:
                raise GDriveSyncError('Could not sync %s because of multiple parents within %s' % (item, drive_dir))

    def get_differences(self, drive_dir, local_dir, skip_dot_files_and_dirs=False, exclude=None):
        """
        Get the difference between local and remote directories
        
        Returns a list of GDriveSyncDifference objects
        """
        self.log('\nGetting differences between')
        self.log(' local directory: %s' % local_dir)
        self.log(' drive directory: %s' % drive_dir)
        
        local_dir = os.path.expanduser(local_dir)
        if not os.path.isdir(local_dir):
            raise GDriveSyncError('Local directory %s is not found' % os.path.abspath(local_dir))
        
        # List of differences that we find
        differences = []
        
        # Cache of local files and folders of class LocalItem 
        local_data = {}
        
        if exclude is None:
            exclude = []
        
        if skip_dot_files_and_dirs:
            # Exlude dot at start or \. (dos) or  /. (unix) 
            exclude.append('(^|[\\/])\.')
        
        ################################################################################
        # Get the Google Drive directory 
        try:
            self.root.get_child(drive_dir)
        except KeyError:
            # Top level directory does not exist
            #  -> Mark top level directory as missing 
            differences.append(GDriveSyncDifference(GDriveSyncDifference.ONLY_LOCAL,
                                                    local_item=LocalItem(os.path.abspath(local_dir))))
            #  -> Mark everything under the top level directory as missing
            for root, dirs, files in os.walk(unicode(local_dir)):
                for item in files + dirs:
                    pth_loc = os.path.join(root, item) 
                    if self._should_exclude(pth_loc, exclude):
                        # Skip excluded paths
                        continue
                    differences.append(GDriveSyncDifference(GDriveSyncDifference.ONLY_LOCAL,
                                                            local_item=LocalItem(pth_loc)))
            return differences
        
        ################################################################################
        # Find changes between remote and local
        for item, pth in self.walk_syncable(drive_dir):
            pth_loc = os.path.join(local_dir, *pth)
            
            if self._should_exclude(pth_loc, exclude):
                # This matched an exclude pattern
                continue
            
            # Check if the local item is present
            if pth_loc in local_data:
                local = local_data[pth_loc]
            elif os.path.exists(pth_loc):
                local = local_data[pth_loc] = LocalItem(pth_loc)
            else:
                differences.append(GDriveSyncDifference(GDriveSyncDifference.ONLY_REMOTE, remote_item=item))
                continue
            local_data[pth_loc] = local
            
            # Check that local and remote are either both files or both directories 
            if item.is_dir != local.is_dir:
                differences.append(GDriveSyncDifference(GDriveSyncDifference.FILE_DIRECTORY_MISMATCH,
                                                        remote_item=item,
                                                        local_item=local))
                continue
            
            # If the item is a directory it is considered to be equal on remote and local
            if item.is_dir:
                continue
            # If the item has been modified locally after previous upload then files are different
            elif local.modified > item.modified:
                differences.append(GDriveSyncDifference(GDriveSyncDifference.NEWER_LOCAL,
                                                        remote_item=item,
                                                        local_item=local))
                continue
            # If the file sizes differ then the files are different (obviously)
            elif local.file_size != item.file_size:
                print 'Different', local.path, local.file_size, item.file_size
                differences.append(GDriveSyncDifference(GDriveSyncDifference.FILES_ARE_DIFFERENT,
                                                        remote_item=item,
                                                        local_item=local))
                continue
        
        ################################################################################
        # Find items on local disk that are not present on the remote
        for root, dirs, files in os.walk(unicode(local_dir)):
            for item in files + dirs:
                pth_loc = os.path.join(root, item)
                
                if self._should_exclude(pth_loc, exclude):
                    # This matched an exclude pattern
                    continue
                
                # Have we already dealt with this above? In that case it is should be OK
                if pth_loc in local_data:
                    continue

                item = LocalItem(pth_loc)
                if item.file_size == 0:
                    self.log("Can't sync %s, because it is empty" % item, 'warning')
                    continue

                # File or directory is not on Drive
                differences.append(GDriveSyncDifference(GDriveSyncDifference.ONLY_LOCAL, local_item=item))
        
        return differences
    
    def _should_exclude(self, path, exclude_patterns):
        """
        Should this path be excluded?
        """
        for pat in exclude_patterns:
            if re.search(pat, path) is not None:
                self.log('Excluding "%s" due to exclude pattern "%s"' % (path, pat))
                return True
        return False
    
    def log(self, message, flag='info'):
        """
        By default messages are printed to stdin if verbose=True
        """
        prefix = ''
        if flag == 'warning':
            prefix = 'WARNING: '
            self.logged_warnings.append(message)
        elif flag == 'error':
            prefix = 'ERROR: '
            self.logged_errors.append(message)
        if self.verbose:
            print prefix + message
    