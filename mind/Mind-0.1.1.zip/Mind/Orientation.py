"""
Brain.Orientation
by Jakov Mankas
aka. Knowledge
"""

imported_tiled = True
try:
    import tiledtmxloader
except ImportError:
    imported = False


class MapError(Exception):

    def __init__(self, x, y, max_x, max_y):
        self.x = x
        self.y = y
        self.max_x = max_x
        self.max_y = max_y

    def __str__(self):
        self.fin = ''
        if self.x > self.max_x:
            self.fin += 'x should be reduced by ' + str(self.x - self.max_x)
            if self.y > self.max_y:
                self.fin += ', '
        if self.y > self.max_y:
            self.fin += 'y should be reduced by ' + str(self.y - self.max_y)
        return self.fin


class MAP:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.objects = []

    def __repr__(self):
        if self.objects:
            self.fin = ''
            self.count = 1
            for obj in self.objects:
                self.fin += str(self.count) + '. ' + str(obj) + '\n'
                self.count += 1
            return self.fin[:-1]
        else:
            return 'Empty map'

    def __contains__(self, item):
        self.item = item
        return self.item in self.objects
        
    def __bool__(self):
        return bool(self.objects)

    def add_obj(self, obj):
        self.obj = obj
        if type(self.obj) == point:
            if self.obj.x > self.width or self.obj.y > self.height:
                raise MapError(obj.x, obj.y, self.width, self.height)
        self.objects.append(self.obj)

    def at(self, x, y):
        self.x = x
        self.y = y
        for obj in self.objects:
            if type(obj) == point:
                if obj.x == self.x and obj.y == self.y:
                    yield obj
            elif type(obj) == group_of_points:
                self.T = False
                for POINT in obj.at(self.x, self.y):
                    yield POINT
                    self.T = True
                if self.T:
                    yield obj


class point:

    def __init__(self, x, y, Map, description='Unknown'):
        self.x = x
        self.y = y
        self.Map = Map
        self.description = description
        self.Map.add_obj(self)

    def __str__(self):
        return self.description + ' @ ' + str(self.x) + ', ' + str(self.y)


class group_of_points:

    def __init__(self, Map, description='Unknown', *points):
        self.Map = Map
        self.description = description
        self.points = points
        self.counter = 0
        for x in range(len(self.Map.objects)):
            if self.Map.objects[x - self.counter] in self.points:
                del self.Map.objects[x - self.counter]
                self.counter += 1
        self.Map.add_obj(self)

    def __str__(self):
        self.fin = self.description + ' group ['
        for Point in self.points:
            self.fin += str(Point) + '; '
        self.fin = self.fin[:-1] + ']'
        return self.fin

    def at(self, x, y):
        self.x = x
        self.y = y
        for Point in self.points:
            if Point.x == self.x and Point.y == self.y:
                yield Point
