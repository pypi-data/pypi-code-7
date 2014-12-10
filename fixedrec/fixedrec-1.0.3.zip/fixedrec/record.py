from .utils import n_, pset


class Record(object):
    """Record base class, providing attribute access and pretty printing.

       Usage::
       
            @register_record
            class StatusRecord(Record):
                RECTYPE = 'ver'
                layout = Layout(
                    '=4sQ10sH12xHcc',
                    'rectype',
                    'timestamp',
                    'version',
                    'reclen',
                    'pad'
                    'chksum',
                    'cr',
                    'nl',
                    name="StatusRecord"
                )

                def __init__(self, data=None, **kw):
                    super(StatusRecord, self).__init__(
                        StatusRecord.layout, data, **kw
                    )
                    if data is None:
                        self.rectype = StatusRecord.RECTYPE
                        self.version = '1.0.0'
                        self.reclen = len(StatusRecord.layout)
                        self.cr = b'\\r'
                        self.nl = b'\\n'
                    self.set_checksum()
                
                def set_checksum(self):
                    # checksum of all preceeding fields.
                    cksm_field = self._layout['chksum']
                    cksm = utils.bsd_checksum(self._data[:cksm_field.position])
                    cksm_field.set_value(self._data, cksm)

    """
    def __init__(self, layout, data=None, **kw):
        """`layout` should be a :class:`Layout` object.
           `data` should be raw data read from file.
           `**kw` can be used to set field values directly.
        """
        self._layout = layout
        self._data = bytearray(data if data is not None else len(self._layout))

        # set individual fields
        for k, v in kw.items():
            setattr(self, k, v)

    def __len__(self):
        """The record length is defined by the length of its layout.
        """
        return len(self._layout)

    def __getattr__(self, attr):
        """Get an attribute (note: attributes of Record, or its sub classes
           takes precedence over field names.
        """
        try:
            return super(Record, self).__getattr__(attr)
        except AttributeError:
            return self._layout[attr].get_value(self._data)

    def __setattr__(self, attr, val):
        """All instance variables of Record start with an underscore soas not
           to conflict with any field names.
        """
        if attr.startswith('_') or attr not in self._layout:
            return super(Record, self).__setattr__(attr, val)

        self._layout[attr].set_value(self._data, val)
        return val

    def parts(self):
        """Return data for each field of the layout.
        """
        return self._layout.split(str(self._data))

    def pretty_parts(self):
        """Make binary data more readable by converting padding bytes in string
           fields to underscore (`_`) and padding fields to star (`*`).
        """
        res = []
        for i, p in enumerate(self.parts()):
            if self._layout[i].format == 's':
                res.append(n_(p))
            elif self._layout[i].format == 'x':
                res.append(n_(p, '*'))
            else:
                res.append(p)
        return res

    def __repr__(self):
        return str(self.pretty_parts())

    def as_dict(self):
        """Or at least as close to a dict as we can get and still preserve
           field order.
        """
        parts = self._layout.split(str(self._data))
        return pset(zip(self._layout.names, self.pretty_parts()))
