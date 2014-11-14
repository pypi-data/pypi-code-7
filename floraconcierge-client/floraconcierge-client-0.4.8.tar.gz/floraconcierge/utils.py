from ordered_set import OrderedSet


class LimitedSet(OrderedSet):
    def __init__(self, limit=0, seq=()):
        setattr(self, 'limit', limit)

        super(LimitedSet, self).__init__(seq)

        self._check_length()

    def copy(self):
        return LimitedSet(limit=self.limit, seq=self)

    def discard(self, key):
        self.items.remove(key)
        self.map.pop(key)

    def _check_length(self):
        if not self.limit:
            return

        if len(self) > self.limit:
            for v in self[0:-self.limit]:
                self.remove(v)

    def add(self, key):
        result = super(LimitedSet, self).add(key)

        self._check_length()

        return result

    append = add


