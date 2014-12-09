# -*- coding: utf-8 -*-

"""Hierarchical session wrapper.
   The hierarchy is built around dotted names (a.b.c).
"""


def mkkey(*subkeys):
    "Create a dotted name from the passed subkeys."
    return '.'.join(subkeys)


class DKSession(object):
    """Hierarchical wrapper around session store.
    """
    
    def __init__(self, request, key):
        self._request = request
        self._session = request.session
        self._key = key

    def __str__(self):
        items = ['    %s : %s' % kv for kv in self._session.items()]
        return 'Session(\n' + '\n'.join(items) + '\n)'

    def __repr__(self):
        vals = ', '.join('%s: %s' % (k, repr(v))
                         for k,v in self._session.items())
        return '<DKSession(%s)>' % vals

    def __getstate__(self):  # pylint:disable=R0201
        "Cannot pickle sessions."
        return None

    def get(self, subkey, default=None):
        "Analogous to dict.get()."
        key = mkkey(self._key, subkey)
        return self._session.get(key, default)

    def pop(self, subkey, default=None):
        """Return the value for the requested key, and remove it from the
           session.
        """
        val = self.get(subkey, default)
        self._remove(subkey)
        return val

    def change(self, subkey, default='', cnvt=None, source=None):
        """Grab new value of session[subkey] from request.REQUEST.
           (too specialized to be in this class?)

           To save the cursor position between posts, in view::

              page.session.change('cursor', default=0)

           In html (using jQuery.caret)::

              // before submit, save the position of the caret in #id_text
              var pos = $('#id_text').caret();
              $('#id_cursor').val(pos);

              // set the value when loading the page (moving the cursor
              // left as an excercise).
              <input type="hidden"
                     name="cursor"
                     id="id_cursor"
                     value="{{ session.cursor }}">

        """
        if source is None:
            source = self._request.REQUEST
        if cnvt is None:
            cnvt = type(default)
            
        val = source.get(subkey)
        if val is None:
            if not self.get(subkey):
                self[subkey] = default
        else:
            self[subkey] = cnvt(val)

    def poplist(self, subkey, default=None):
        "Destructively fetch the last item in the list under ``subkey``."
        lst = self[subkey]
        if lst:
            item = lst.pop()
            self[subkey] = lst
        else:
            item = default
        return item        

    def peeklist(self, subkey):
        "Look at the last item in the list under ``subkey``."
        lst = self.get(subkey, [])
        if len(lst) >= 1:
            return lst[-1]
        return None

    def _remove(self, subkey):
        if subkey in self:
            #print 'removing', subkey
            del self._session[mkkey(self._key, subkey)]
        
    def remove(self, subkey, protected=False):
        """Remove a subkey.  If ``protected`` is True, then it will remove
           all items, even protected items.
        """
        if protected:
            # remove even if protected
            if self.is_protected(subkey):
                p = self.protect_list
                p.remove(subkey)
                self._session[self._pkey] = p

            self._remove(subkey)
        else:
            # remove if not protected
            if not self.is_protected(subkey):
                self._remove(subkey)

    @property
    def _pkey(self):
        return mkkey(self._key, 'protect__')

    def is_protected(self, subkey):
        "Has the subkey been protected from ``remove()``?"
        return subkey in self.protect_list

    def has_key(self, subkey):
        "Analogous to dict.has_key()."
        return mkkey(self._key, subkey) in self._session.keys()

    def __contains__(self, subkey):
        "subkey in self?"
        return self.has_key(subkey)

    def __getitem__(self, subkey):
        return self.get(subkey)

    def __getattr__(self, subkey):
        return self.get(subkey)

    def __setitem__(self, subkey, value):
        self._session[mkkey(self._key, subkey)] = value

    def append(self, lstvar, value):
        "Append value to the subkey lstvar, creating a list if not present."
        lst = self.get(lstvar, [])
        lst.append(value)
        self[lstvar] = lst

    def protect(self, subkey):
        "Protect subtree under ``subkey`` from deletion by ``remove()``."
        p = self.protect_list
        if subkey not in p:
            p.append(subkey)
            self['protect__'] = p

    @property
    def protect_list(self):
        "The list of protected variables."
        if 'protect__' in self:
            return self['protect__']
        else:
            return []
        
    def __delitem__(self, subkey):
        self.remove(subkey)

    def _extract_key(self, combinedkey):
        return combinedkey[len(self._key) + 1:]
    
    def keys(self):
        "Yield all subkeys of this subtree."
        for k in self._session.keys():
            if k != self._pkey and k.startswith(self._key):
                yield self._extract_key(k)

    def __iter__(self):
        return ((k, self[k]) for k in self.keys())

    def clear(self, protected=False):
        "Remove all subitems."
        for k in self.keys():
            self.remove(k, protected)
        if protected:
            self._remove(self._pkey)

    def setitems(self, items):
        for item, value in items:
            self[item] = value
