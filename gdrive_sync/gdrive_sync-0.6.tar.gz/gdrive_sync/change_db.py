import os
import cPickle as pickle
import dateutil.parser
from collections import defaultdict

from . import gdrive_communication as api

class ChangeDB(object):
    def __init__(self, filename, logger=None):
        """
        This class stores the Google Drive file changes. The format of the
        changes is identical with the dictionaries returned by the Google
        Python API code for Google Drive
        """
        self.filename = filename
        if logger is None:
            self.logger = lambda msg, flag=None: None
        else:
            self.logger = logger

        self.database = None
        
    @property
    def changes(self):
        return self.database['changes']
    
    @property
    def max_change_id(self):
        return self.database['max_change_id']
    
    def add_change(self, change):
        """
        Add change to the database
        """
        cid = int(change['id'])
        assert cid not in self.database['changes']
        assert cid > self.database['max_change_id']
         
        self.database['max_change_id'] = cid
        self.database['changes'][cid] = change
    
    def __read(self):
        """
        Load change database from disk
        """
        if os.path.isfile(self.filename):
            # Read database from file
            with open(self.filename, 'rb') as f:
                self.database = pickle.load(f)
        else:
            self.database = {'max_change_id': 0, 'changes': {}}
            self.logger('Creating new change set database')
            # Check that we can write to the database file
            self.__write()
        
        self.logger('Loaded changes database containing %d changes. Last change id is %d' % (len(self.changes), self.max_change_id))
    
    def get_roots(self):
        """
        Replay the stored changes in the database to create a local
        representation of the current state of the remote Drive
        """
        if self.database is None:
            self.__read()

        changes = self.changes
        id_to_obj_map = {}
        deleted = set()
        if not changes:
            return GDriveDirectory(None, None)
        
        keys = sorted(changes.keys())
        sorted_changes = [self.changes[cid] for cid in keys]
        
        roots = []
        
        for c in sorted_changes:
            fid = c['fileId']
            if c.get('deleted', False):
                if fid in id_to_obj_map:
                    obj = id_to_obj_map[fid]
                    obj.delete()
                    del id_to_obj_map[fid]
                else:
                    pass
                    #print 'Object to delete is not in map', c
                deleted.add(fid)
                continue
                
            f = c['file']
            assert f['id'] == fid

            parents = list()

            for parent in f['parents']:
                parent_id = parent['id']

                if parent_id in id_to_obj_map:
                    parents.append(id_to_obj_map[parent_id])
                else:
                    p_temp = GDriveDirectory({'id': parent_id}, [])
                    parents.append(p_temp)
                    id_to_obj_map[parent_id] = p_temp
                    #print 'Found unrooted object %s' % f['title'], fid
                    roots.append(p_temp)
            
            if fid in id_to_obj_map:
                obj = id_to_obj_map[fid]
                if obj.is_root:
                    #print 'Rooting object %s' % f['title'], fid
                    roots.remove(obj)
                obj.update(f, parents)
            else:
                if f['mimeType'] == api.MIME_DIRECTORY:
                    obj = GDriveDirectory(f, parents)
                else:
                    obj = GDriveFile(f, parents)

                for p in parents:
                    p.add_child(obj)

                id_to_obj_map[fid] = obj
        
        roots = [s for s in roots if s.id not in deleted]

        return roots

    def get_file_tree(self, root_id=None, include_trashed=False):
        roots = self.get_roots()
        root = None
        for r in roots:
            if r.id == root_id:
                root = r
                break

        assert root.is_root
        assert len(root.parents) == 0

        # Remove trashed before verify - it might be duplicates where one is trashed and the other not
        if not include_trashed:
            root.remove_all_trashed()
        
        # Check that everything is OK with the constructed file tree
        root.verify(self.logger)
        
        return root
    
    def __write(self):
        """
        Save change database to disk
        """
        with open(self.filename, 'wb') as f:
            pickle.dump(self.database, f, protocol=pickle.HIGHEST_PROTOCOL)
        self.logger('Saved changes database containing %d changes. Last change id is %d' % (len(self.changes), self.max_change_id))
    
    def __enter__(self):
        """
        Allow the database to be used as a context manager
        """
        self.__read()
        return self
    
    def __exit__(self, *argv):
        """
        Allow the database to be used as a context manager
        make sure that the database is saved to disk
        """
        self.__write()
        if argv[0] is not None:
            self.logger('Emergency saved changes database due to exception')

class GDriveFile(object):
    is_file = True
    is_dir = False
    is_deleted = False
    
    def __init__(self, info, parents=None):
        self.parents = [] if parents is None else parents
        self.info = info
        self.is_root = len(self.parents) == 0
    
    @property
    def id(self):
        return self.info['id']

    def __str__(self):
        p = self.path
        if len(p) == 1:
            return p[0]
        else:
            return str(p)

    @property
    def name(self):
        if self.is_root:
            return '/'
        
        orig = self.info.get('originalFilename', None)
        title = self.info.get('title', None)
        ext = self.info.get('fileExtension', None)
        
        if orig:
            return orig
        elif ext and title.endswith(ext):
            return title
        elif ext:
            return '%s.%s' % (title, ext)
        else:
            return title
    
    @property
    def path(self):
        "The full path to this drive item"
        if self.is_root:
            return ['']

        paths = []
        for parent in self.parents:
            for p in parent.path:
                paths.append(p + "/" + self.name)

        return paths

    @property
    def modified(self):
        isotime = self.info['modifiedDate'] # Format: 2013-01-16T15:07:34.915Z
        return dateutil.parser.parse(isotime)
    
    @property
    def file_size(self):
        size = self.info['fileSize']
        return int(size)
    
    @property
    def is_trashed(self):
        return self.info['labels']['trashed']
    
    def delete(self):
        if self.parents is not None:
            for p in self.parents:
                p.unlink_child(self)

        self.is_deleted = True
    
    def update(self, new_info, new_parents):
        # Swap parents if necessary
        assert len(new_info['parents']) == len(new_parents)

        new_parent_ids = [p['id'] for p in new_info['parents']]
        for new_parent_id in new_parent_ids:
            assert new_parent_id in [p.id for p in new_parents]

        current_parent_ids = []
        if self.is_root:
            assert 'parents' not in self.info
            assert len(self.parents) == 0
        else:
            # check whether the parent information is consistent
            current_parent_ids = set([p['id'] for p in self.info['parents']])
            self_parent_ids = set([p.id for p in self.parents])
            assert len(current_parent_ids.symmetric_difference(self_parent_ids)) == 0

        if set(new_parent_ids) != set(current_parent_ids):
            self._swap_parents(new_parents)
        
        # Update information
        self.is_root = False # root object will never be updated
        self.info = new_info
    
    def _swap_parents(self, new_parents):
        for p in self.parents:
            p.unlink_child(self)

        if new_parents is not None:
            for p in new_parents:
                p.add_child(self)

            self.is_root = False
        else:
            self.is_root = True

        self.parents = new_parents
    
    def verify(self, logger):
        assert self.info is not None
        assert not self.is_deleted
        if self.is_root:
            assert self.is_dir and not self.is_file
            assert len(self.parents) == 0
        else:
            assert len(self.parents) > 0
            assert all([self.id in p.children for p in self.parents])

            for parent in self.parents:

                if not parent.is_root:
                    assert parent.id in [p['id'] for p in self.info['parents']]
        
            if self.is_dir:
                assert not self.is_file
                assert self.info['mimeType'] == api.MIME_DIRECTORY
            else:
                assert self.is_file
                assert self.info['mimeType'] != api.MIME_DIRECTORY

class GDriveDirectory(GDriveFile):
    is_file = False
    is_dir = True
    
    def __init__(self, info, parents):
        super(GDriveDirectory, self).__init__(info, parents)
        self.children = {}
    
    def get_children(self):
        return self.children.values()            
            
    def add_child(self, child):
        self.children[child.info['id']] = child
    
    def unlink_child(self, child):
        del self.children[child.info['id']]
    
    def get_child(self, path):
        """
        Get a child or a grand child, great grand child etc. The path
        is interpreted in the Unix manner with separator '/'
        """
        if '/' in path:
            # This is a path to a sub-directory
            pth_elems = path.split('/')
            if pth_elems[0] == '':
                assert self.is_root
                pth_elems = pth_elems[1:]
            
            elem = self
            for name in pth_elems:
                if not elem.is_dir:
                    raise KeyError('Item "%s" is a file, not a directory' % elem.path)
                if name == '':
                    continue
                elem = elem[name]
            return elem
        else:
            # This is a name to a item in this directory
            for c in self.children.itervalues():
                if c.name == path:
                    return c
            raise KeyError('Item "%s" in "%s" not found on Drive' % (path, self.path))
    __getitem__ = get_child
    
    def has_file(self, filename):
        for c in self.children.itervalues():
            if c.name == filename:
                return c.is_file
        return False
    
    def has_dir(self, filename):
        for c in self.children.itervalues():
            if c.name == filename:
                return c.is_dir
        return False
    
    def remove_all_trashed(self):
        stack = self.children.values()
        while stack:
            item = stack.pop()
            if item.is_trashed:
                item.delete()
            if item.is_dir:
                stack.extend(item.children.itervalues())
    
    def verify(self, logger):
        super(GDriveDirectory, self).verify(logger)        
        names = defaultdict(list)
        for cid, c in self.children.iteritems():
            assert cid == c.info['id']
            names[c.name].append(c)
            
            if self not in c.parents:
                print 'Item "%s" claims "%s" as its parents, but is found in "%s"' % (c.name, c.parent.path, self.path)
            
            c.verify(logger)
        
        for name, children in names.iteritems():
            if len(children) == 1:
                continue
            logger('There are %d items called "%s" on Drive in "%s"' % (len(children), name, self.path), 'warning')
