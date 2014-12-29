class _BaseOffsetTracker(object):
    def __init__(self):
        self._offsets = {}
        self.is_modified = False

    def get(self, topic, partition):
        return self._offsets.get((topic, partition), 0)

    def set(self, topic, partition, offset):
        raise NotImplementedError()

    def force_set(self, topic, partition, offset):
        if not self.is_modified:
            self.is_modified = self._offsets.get((topic, partition)) != offset
        self._offsets[(topic, partition)] = offset

    def __iter__(self):
        return iter(self._offsets.items())

    def window(self):
        pass

    def commit(self):
        self.is_modified = False


class SimpleOffsetTracker(_BaseOffsetTracker):
    def set(self, topic, partition, offset):
        self.force_set(topic, partition, offset)


class WindowedOffsetTracker(_BaseOffsetTracker):
    def __init__(self):
        _BaseOffsetTracker.__init__(self)
        self._new_offsets = {}

    def set(self, topic, partition, offset):
        self._new_offsets[(topic, partition)] = offset

    def window(self):
        self.is_modified = self._offsets != self._new_offsets
        self._offsets = self._new_offsets
