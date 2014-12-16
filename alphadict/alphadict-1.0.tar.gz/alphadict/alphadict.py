from collections import OrderedDict


class AlphaDict(OrderedDict):

    def __setitem__(self, *args, **kwargs):
        ret = super(AlphaDict, self).__setitem__(*args, **kwargs)
        self.__sort_my_thing()
        return ret

    def __sort_my_thing(self):
        sorted = self.key_sort()
        for k, v in sorted.iteritems():
            del self[k]
            super(AlphaDict, self).__setitem__(k, v)

    def key_sort(self):
        out = OrderedDict()
        for k, v in sorted(self.items()):
            if isinstance(v, dict):
                out[k] = self.__class__(v)
            elif isinstance(v, list):
                out[k] = self._handle_list(v)
            else:
                out[k] = v
        return out

    def _handle_list(self, v):
        _v_out = []
        for _v in v:
            if isinstance(_v, dict):
                _v_out.append(self.__class__(_v))
            elif isinstance(_v, list):
                _v_out.append(self._handle_list(_v))
            else:
                _v_out.append(_v)
        return _v_out

