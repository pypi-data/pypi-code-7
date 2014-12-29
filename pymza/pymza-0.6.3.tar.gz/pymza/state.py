import os
import json
import collections

import leveldb


class StateManager(object):
    def __init__(self, state_dir):
        self.state_dir = state_dir
        self.task_states = {}
        self.task_offsets = {}

    def get_state(self, task):
        if isinstance(task, basestring):
            task_name = task
        else:
            task_name = task.name

        state = self.task_states.get(task_name)
        if state is None:
            task_state_path = os.path.join(self.state_dir, task_name)
            state = TaskState(task_name, task_state_path)
            self.task_states[task_name] = state
        return state

    def get_offset_store(self, task):
        if isinstance(task, basestring):
            task_name = task
        else:
            task_name = task.name

        store = self.task_offsets.get(task_name)
        if store is None:
            offset_store_path = os.path.join(self.state_dir, task_name, 'offsets')
            store = OffsetStore(task_name, offset_store_path)
            self.task_offsets[task_name] = store
        return store


class OffsetStore(object):
    def __init__(self, task_name, state_dir):
        self.task_name = task_name

        if not os.path.exists(state_dir):
            os.makedirs(state_dir)  
            
        self.db = leveldb.LevelDB(state_dir)

    def load(self, offsets):
        for key, val in self.db.RangeIter():
            topic, partition = key.split(':', 1)
            partition = int(partition)
            offset = int(val)
            offsets.force_set(topic, partition, offset)

    def save(self, offsets):
        batch = leveldb.WriteBatch()
        for (topic, partition), offset in offsets:
            batch.Put('{0}:{1}'.format(topic, partition), str(offset))
        self.db.Write(batch, sync=True)            


class TaskState(collections.MutableMapping):
    def __init__(self, task_name, state_dir):
        self.task_name = task_name

        if not os.path.exists(state_dir):
            os.makedirs(state_dir)  
            
        self.db = leveldb.LevelDB(state_dir)
        self._cache = {}
        self._deletes = set()
        self._changes = set()

    def __getitem__(self, key):
        if key in self._cache:
            return self._cache[key]
        else:
            value = json.loads(self.db.Get(key))
            self._cache[key] = value
            return value

    def __setitem__(self, key, value):
        self._deletes.discard(key)
        self._cache[key] = value
        self._changes.add(key)

    def __delitem__(self, key):
        if key in self._cache:
            del self._cache[key]
        self._deletes.add(key)
        self._changes.discard(key)

    def __iter__(self):
        return self.iterkeys()

    def __len__(self):
        raise RuntimeError('Calculating length of state is not supported')        

    # expose RangeIter api
    def range(self, *args, **kwargs):
        include_value = kwargs.get('include_value', True)

        if not include_value:
            return self.db.RangeIter(*args, **kwargs)
        else:
            return ((k, json.loads(v)) for k, v in self.db.RangeIter(*args, **kwargs))

    # improved methods
    def iteritems(self):
        return self.range()

    def iterkeys(self):
        return self.range(include_value=False)

    def itervalues(self):
        for (k, v) in self.iteritems():
            yield v

    def keys(self):
        # fixes default method which calls __len__
        return list(self.iterkeys())

    def values(self):
        return list(self.itervalues())

    def has_key(self, key):
        return key in self    

    @property
    def is_modified(self):
        return self._changes or self._deletes

    def commit(self):
        batch = leveldb.WriteBatch()
        for key in self._changes:
            batch.Put(key, json.dumps(self._cache[key]))
        for key in self._deletes:
            batch.Delete(key)
        self.db.Write(batch, sync=True)
        self._changes = set()
        self._deletes = set()

    def clear(self):
        for key in self.iterkeys():
            del self[key]
