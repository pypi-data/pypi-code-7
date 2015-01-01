"""
Mind.Orientation
by Jakov Mankas
aka. Knowledge
"""

imported_tiled = True
try:
    import tiledtmxloader
except ImportError:
    imported_tiled = False


class MapError(Exception):
    """exception for points outside the map"""

    def __init__(self, x, y, max_x, max_y):
        self.x = x
        self.y = y
        self.max_x = max_x
        self.max_y = max_y

    def __str__(self):
        self.fin = ''
        if self.x > self.max_x:
            self.fin += 'x should be reduced by ' + str(self.x -
            self.max_x)
            if self.y > self.max_y:
                self.fin += ', '
        if self.y > self.max_y:
            self.fin += 'y should be reduced by ' + str(self.y -
            self.max_y)
        return self.fin


class MAP:
    """bacis map class"""

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
            elif type(obj) == rect:
                if obj.at(self.x, self.y):
                    yield obj


class point:
    """basic point class"""

    def __init__(self, x, y, Map, description='Unknown'):
        self.x = x
        self.y = y
        self.Map = Map
        self.description = description
        self.Map.add_obj(self)

    def __str__(self):
        return self.description + ' @ ' + str(self.x) + ', ' + str(self.y)


class group_of_points:
    """class for group of points"""

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
        self.fin = self.fin[:-2] + ']'
        return self.fin

    def at(self, x, y):
        self.x = x
        self.y = y
        for Point in self.points:
            if Point.x == self.x and Point.y == self.y:
                yield Point


class rect:
    """bacis map rect class"""

    def __init__(self, x, y, width, height, Map, description='Unknown'):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.Map = Map
        self.Map.add_obj(self)
        self.description = description

    def __repr__(self):
        return self.description + ' rect ' + str(self.width) + 'X' + \
        str(self.height) + ' @ ' + str(self.x) + ', ' + str(self.y)

    def __contains__(self, item):
        self.item = item
        if type(self.item) == point:
            if self.at(self.item.x, self.item.y):
                return True
        elif type(self.item) == group_of_points:
            for p in self.item.points:
                if not p in self:
                    return False
            return True
        elif type(self.item) == rect:
            if self.x <= self.item.x and self.y <= self.item.y and self.x \
            + self.width >= self.item.x + self.item.width and self.y + \
            self.height >= self.item.y + self.item.height:
                return True
            return False
        else:
            raise TypeError("'in <rect>' doesn't support " +
            repr(self.item))

    def at(self, x, y):
        return self.x + self.width >= x >= self.x and self.y + \
        self.height >= y >= self.y

if imported_tiled:

    class tiled_map:
        """class for map in tiled"""

        def __init__(self, name):
            self.name = name
            self.out_map = tiledtmxloader.tmxreader.TileMapParser().\
            parse_decode(self.name + '.tmx')
            self.out_objects = tiledtmxloader.helperspygame.\
            ResourceLoaderPygame()
            self.out_objects.load(self.out_map)
            self.renderer = tiledtmxloader.helperspygame.RendererPygame()
            self.layers = tiledtmxloader.helperspygame.\
            get_layers_from_map(self.out_objects)
            self.in_map = MAP(self.out_map.pixel_width,
            self.out_map.pixel_height)
            for layer in self.layers:
                if layer.is_object_group:
                    for obj in layer.objects:
                        if obj.name:
                            self.in_map.add_obj(rect(obj.x, obj.y,
                            obj.width, obj.height, self.in_map, obj.name))
                        else:
                            self.in_map.add_obj(rect(obj.x, obj.y,
                            obj.width, obj.height, self.in_map))

        def __repr__(self):
            return repr(self.in_map)

        def set_screen(self, screen):
            self.screen = screen
            self.screen_w, self.screen_h = self.screen.get_size()
            self.renderer.set_camera_position_and_size(0, 0, self.screen_w, self.screen_h)

        def set_camera_pos(self, x, y, edge=True):
            self.x = x
            self.y = y
            self.edge = edge
            if self.edge:
                self.x = max([self.screen_w / 2, min([self.x, self.in_map.width - self.screen_w / 2])])
                self.y = max([self.screen_h / 2, min([self.y, self.in_map.height - self.screen_h / 2])])
            self.renderer.set_camera_position(self.x, self.y)
            return (self.x, self.y)

        def blit(self):
            for layer in self.layers:
                if not layer.is_object_group:
                    self.renderer.render_layer(self.screen, layer)
