from datetime import datetime
from vectortile import TypedMatrix


class Tile(object):
    def __init__(self, typedmatrix_str, meta=None):
        """

        :param typedmatrix_str: a packed string as returned by TypedMatrix.pack()
        """
        self.typedmatrix_str = typedmatrix_str
        if not meta:
            meta = dict()
        self.meta = meta

    @staticmethod
    def fromdata(data, meta=None, columns=None):
        """

        :param data: a dict or list of dicts suitable for TypedMatrix.pack()
        :param meta: a dict of meta data fields
        :return: a Tile object
        """
        if not meta:
            meta = dict()
        return Tile(TypedMatrix.pack(data, extra_header_fields=meta, columns=columns, orientation='columnwise'), meta=meta)

    @staticmethod
    def nodata(complete_ancestor_bounds=None):
        meta = dict(nodata=True)
        if complete_ancestor_bounds:
            meta['complete_ancestor'] = str(complete_ancestor_bounds.get_bbox())
        return Tile.fromdata(data=dict(), meta=meta)

    def is_nodata(self):
        return 'nodata' in self.meta

    def complete_ancestor(self):
        return self.meta.get('complete_ancestor')

    @staticmethod
    def timestamp(dt=datetime.now()):
        """
        Create a coded UTC timestamp from a datetime using the internal coding format used in packed tiles
        """
        return TypedMatrix.get_utc_timestamp(dt)

    def unpack(self):
        return TypedMatrix.unpack(self.typedmatrix_str)

    def __str__(self):
        return "%s" % self.typedmatrix_str

    def __repr__(self):
        return "%s(%s,meta=%s)" % (self.__class__.__name__, repr(self.typedmatrix_str), repr(self.meta))

    @property
    def size(self):
        return len(self.typedmatrix_str)

    def asdict(self):
        header, data = self.unpack()
        header['data'] = data
        return header
