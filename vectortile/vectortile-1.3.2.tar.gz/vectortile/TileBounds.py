import math
import quadtree

from Bbox import Bbox

class TileBounds(object):
    maxzoom = 21
    worldwidth = 360.0
    worldheight = 180.0
    min_tile_width = worldwidth / pow(2, maxzoom)
    min_tile_height = worldheight / pow(2, maxzoom)

    def __init__(self, gridcode=''):
        """
        gridcode value of '' (empty string) is the world tile Bbox(-180, -90, 180, 90)
        """
        self.gridcode = gridcode

    @staticmethod
    def world_bounds():
        return TileBounds()

    @classmethod
    def from_string(cls, s):
        return cls(gridcode=s)

    @classmethod
    def from_bbox_best_fit(cls, bbox):
        """
        Return a TileBounds that is about the same size as the bbox and contains the center point
        """
        # get the zoom level based on the width of the given bounding box
        level = min(cls.maxzoom,
                    max(0,
                        int(math.floor(min(
                            math.log(cls.worldwidth / max(bbox.width, cls.min_tile_width), 2),
                            math.log(cls.worldheight / max(bbox.height, cls.min_tile_height), 2))))
                    )
        )
        return cls(gridcode=quadtree.encode(bbox.latmin + bbox.height / 2, bbox.lonmin + bbox.width / 2, level))

    @classmethod
    def from_point(cls, lon, lat, zoom_level):
        assert 0 <= zoom_level <= cls.maxzoom
        # lon==180 is not in the quad tree, because tiles only contian points on the left and bottom edges
        # points on the top and right edges belon to the adjacent tile
        # quadtree will throw if you give it lon==180, so we map it to -180 here
        if lon == 180.0:
            lon = -180.0

        # lat==90 is also a problem because this is always on the top egde of the tile, but we can't wrap
        # around, so instead we fudge it down by half the height of the smallest possible tile
        if lat == 90.0:
            lat = 90 - (cls.min_tile_height / 2)
        return cls(gridcode=quadtree.encode(lat=lat, lon=lon, precision=zoom_level))

    def get_bbox(self):
        bounds = quadtree.bbox(self.gridcode)
        return Bbox(bounds['w'], bounds['s'], bounds['e'], bounds['n'])

    def get_center(self):
        """
        Get the point at the center of the tile
        """
        return self.get_bbox().center

    def get_parent(self):
        if self.gridcode:
            return TileBounds(gridcode=self.gridcode[:-1])

    def get_children(self):
        return [TileBounds(gridcode=self.gridcode + digit) for digit in '0123']

    def get_ancestors(self):
        return [TileBounds(gridcode=self.gridcode[:-i]) for i in range(1, len(self.gridcode) + 1)]

    def contains_point(self, lon, lat):
        return self == TileBounds.from_point(lon, lat, self.zoom_level)

    @property
    def zoom_level(self):
        return len(self.gridcode)

    def __str__(self):
        return self.gridcode

    def __repr__(self):
        return "%s('%s')" % (self.__class__.__name__, str(self))

    def __eq__(self, other):
        return str(self) == str(other)
