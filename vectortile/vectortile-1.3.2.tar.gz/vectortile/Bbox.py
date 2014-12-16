class Bbox(object):
    def __init__(self, lonmin=-180, latmin=-90, lonmax=180, latmax=90):
        self.latmin = float(min(latmin, latmax))
        self.latmax = float(max(latmin, latmax))
        self.lonmin = float(min(lonmin, lonmax))
        self.lonmax = float(max(lonmin, lonmax))

    @classmethod
    def fromstring(cls, s):
        """Initialize Bbox from a string formatted by str()
        """
        return cls(*[float(item) for item in s.split(",")])

    def __str__(self):
        def f(v):
            # Format v as javascript toString():
            if (v == 0.0): return "0"
            return str(v).rstrip("0").rstrip(".")

        # left,bottom,right,top - all according to openlayers :)
        return "%s,%s,%s,%s" % (f(self.lonmin), f(self.latmin), f(self.lonmax), f(self.latmax))

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, str(self))

    @property
    def height(self):
        return self.latmax - self.latmin

    @property
    def width(self):
        return self.lonmax - self.lonmin

    def contains(self, lon, lat):
        """
        Return True if the given point is inside the bbox, False if not.
        Note that a point exactly on the left or bottom edge of the bbox is consider inside, while a point
        exactly on the right or top edge is not.  the point on the lower left corner is inside (True), all 3 other
        corner points are outside (False)
        """
        return self.lonmin <= lon < self.lonmax and self.latmin <= lat < self.latmax

    def __eq__(self, other):
        return self.lonmin == other.lonmin and \
                self.lonmax == other.lonmax and \
                self.latmin == other.latmin and \
                self.latmax == other.latmax

    def asdict(self):
        return self.__dict__

    @property
    def center (self):
        """
        Get the point at center of the bbox

        :rtype : dict(lon=lon, lat=lat)
        """
        return dict(lon=self.lonmin + (self.width/2), lat=self.latmin+ (self.height/2))
