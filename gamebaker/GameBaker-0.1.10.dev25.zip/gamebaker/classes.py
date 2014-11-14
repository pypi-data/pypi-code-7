"""
Contains classes used by Game Baker.
"""

import os.path
import math
from itertools import chain

import numpy

import pygame
from pygame.locals import *
pygame.init()
window = pygame.display.set_mode((1000, 1000))

from gamebaker import constants

class Blueprint:
    """
    Parent class for developer-defined classes representing game objects.
    Classes inheriting from ``Blueprint`` should be stored in the ``blueprints.py`` file of a project.
    
    Class variables:
    
    - ``sprite`` - a ``Sprite`` instance that instances of a ``Blueprint`` will be drawn as.
    - ``bounding_box_width``, ``bounding_box_height`` - integers giving the height of the bounding box of instances of a Blueprint in pixels.
    - ``bounding_box_left``, ``bounding_box_top`` (default values 0) - integers giving the top and left of the bounding box
    - ``draw_depth`` (default value 0) - an integer giving the order instances of a Blueprint will be drawn in
                                         Instances with lower values will be drawn first (behind others).
                                         
    - ``possible_collisions`` - a tuple of Blueprints, instances of which should be checked for collisions with instances of this class
    
    Example use::
    
        class MetalBlock(Blueprint):
            sprite = Sprite("metal_block.png")
            bounding_box_width = bounding_box_height = 32
        
            def key_up_press(self):
                self.yspeed -= 1
        
    """
    sprite = None
    bounding_box_top = 0
    bounding_box_left = 0
    bounding_box_width = None
    bounding_box_height = None
    draw_depth = 0
    possible_collisions = set()
    
    grid = None
        
    @staticmethod
    def reset_position(instance):
        """
        Move and instance back to its previous coordinates.
        """
        instance.x = instance.old_x
        instance.y = instance.old_y
                    
    def __init__(self, x, y):
        self._x = x
        self._y = y
        self._old_x = x
        self._old_y = y
        self.xspeed = 0
        self.yspeed = 0
        
    @property
    def old_x(self):
        return self._old_x
    
    @property
    def old_y(self):
        return self._old_y
        
    @property
    def x(self):
        return self._x
        
    @x.setter
    def x(self, value):
        Blueprint.grid.move(self, value, self.y)
        self._x = value
        
    @property
    def y(self):
        return self._y
        
    @y.setter
    def y(self, value):
        Blueprint.grid.move(self, self.x, value)
        self._y = value
        
    def tick(self):
        self.x += self.xspeed
        self.y += self.yspeed
        
    def end_tick(self):
        self._old_x = self.x
        self._old_y = self.y 
        
    def collide(self, other):
        """
        The event called when an instance collides with another.
        """
        pass
        
    def get_rect(self):
        return pygame.Rect(self.x + self.bounding_box_left, self.y + self.bounding_box_top,
                           self.bounding_box_width, self.bounding_box_height)
        
# events dictionary contains all the inbuilt events.
# used by `get_events` in `game.py`.
events = {"__init__", "tick", "begin_tick", "collide", "end_tick"}
doubletap_events = set()

for event in ("_press", "_release", "_held", "doubletap"):
    for method_name in chain(constants.key_constants1.values(), constants.key_constants2.values()):
        events.add(method_name + event)
        doubletap_events.add(method_name + "_doubletap")

def rotate_centre(image, angle):
    """
    Rotate an image while keeping its centre and size.
    """
    original_rect = image.get_rect()
    rotated_image = pygame.transform.rotate(image, angle)
    rotated_rect = original_rect.copy()
    rotated_rect.center = rotated_image.get_rect().center
    rotated_image = rotated_image.subsurface(rotated_rect).copy()
    return rotated_image
    
class Scenery:
    """
    Parent class for developer-defined classes representing objects that don't interact with anything.
    ``Scenery`` subclass instances are drawn, but cannot react to events.
    ``Scenery`` should be used instead of ``Blueprint`` where possible, in order to save memory.
    """
    sprite = None
    draw_depth = 0
    grid = None
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        

class Sprite:
    """
    Represents an image used in the game.
    
    Example use::
    
        a_blueprint_sprite = Sprite(os.path.join("path", "to", "file"))
    """
    def __init__(self, path_to_file):
        self.image = pygame.image.load(os.path.join("images", path_to_file)).convert_alpha()
        self.original_image = pygame.image.load(os.path.join("images", path_to_file)).convert_alpha()
        self.path_to_file = path_to_file
        self.angle = 0
        
    def set_angle(self, angle):
        """
        Point the sprite in a certain direction.
        """
        self.image = rotate_centre(self.original_image, angle)
        
    def __repr__(self):
        return "Sprite({})".format(path_to_file)

class View:
    """
    Represents an area of the game world, and its representation on screen.
    By default, only instances within a ``View`` (or the active border around one) are treated as existing.
    
    Example use::
    
        View(0, 0, 640, 480, 160, 0, 0)
        
    ``variables.mouse_x`` and ``variables.mouse_y`` are relative to the first ``View`` in a level's list.
    """
    def __init__(self, x, y, width, height, active_border, screen_x, screen_y):
        """
        ``x`` - initial x position of the ``View`` in the game world
        ``y`` - initial y game world position
        ``width`` - width of the ``View``, both in the game world and on the screen, in pixels
        ``height`` - height of the ``View``
        ``active_border`` - area around the ``View`` in which instances are treated as existing
        ``screen_x`` - initial x position of the ``View`` on screen
        ``screen_y`` - initial y onscreen position
        """
        self.x = x
        self.y = y
        self.active_border = active_border
        self.width = width
        self.height = height
        self.left = x - active_border
        self.top = y - active_border
        self.right = x + width + active_border
        self.bottom = y + height + active_border
        self.screen_x = screen_x
        self.screen_y = screen_y
        
        self.surface = pygame.Surface((self.width, self.height))
    
    def update_variables(self):
        """
        Update self.left, self.top etc.
        """
        self.left = self.x - self.active_border
        self.top = self.y - self.active_border
        self.right = self.x + self.width + self.active_border
        self.bottom = self.y + self.height + self.active_border
        
    def get_active(self, object):
        """
        Return if an instance is within the view.
        """
        return (self.left <= object.x <= self.right) and (self.top <= object.y <= self.bottom)

        
class Level:
    """
    Represent a single level or area within the game.    
    Levels should be stored in ``levels.py``, in a list assigned to ``levels``.
    
    Example use::
    
        Level([Player(0, 0), Enemy(0, 0, "red")], [Cloud(32, 32)], [View(0, 0, 320, 320, 0, 0, 0)])
    """
    def __init__(self, objects, scenery, views, width, height):
        self.objects = objects
        self.scenery = scenery
        self.views = views
        self.width = width
        self.height = height

class Variables:
    """
    Contain variables used by blueprints, for instance, the coordinates of the mouse.
    """
    pass
        
class Version:
    """
    Record version numbers of games.

    Version mostly follows the format of the Python version numbers (see the general FAQ):
    major.minor.micro

    This is then followed by the build type, which should either be blank, for a release, or one of the following:
    dev(elopment), which precedes
    a(lpha), which precedes
    b(eta), which precedes
    (release) c(andidate), which precedes
    r(elease)

    If the build type is release, then str(version) doesn't show it or the build number.

    The build type suffix is then followed by the build number. This will increases automatically each time the project is built.
    """
    def __init__(self, major, minor, micro, build_type=None, build_number=None):
        self.major = int(major)
        self.minor = int(minor)
        self.micro = int(micro)
        self.build_type = build_type if build_type in ("a", "b", "c", "r") else "dev"
        self.build_number = int(build_number) if build_number else 0

    def __str__(self):
        if self.build_type == "r":
            return "{}.{}.{}".format(self.major, self.minor, self.micro)
        else:
            return "{}.{}.{}{}{}".format(self.major, self.minor, self.micro,
                                     self.build_type if self.build_type else "",
                                     self.build_number if self.build_type else "")
        
class Settings:
    """
    Store the game settings.
    
    Used in a project's ``settings.py``.
    A ``Settings`` object should be assigned to the variable ``settings`` in that file.
    """
    def __init__(self, game_name="", game_version=Version(0, 0, 0, "dev", 0),
                       window_width=480, window_height=480,
                       game_speed=60,
                       active_count=5, sector_size=160):
        """
        ``game_name`` - the name of the game
        ``game_version`` - a ``Version`` object containing the current version
        ``window_width``, ``window_height`` - the width and height of the game window
        ``game_speed`` - the maximum FPS (frames per second) rate
        ``active_count`` - the numbers of steps that go by before a new list of active instances is created
        ``sector_size`` - the width and height of sectors used to speed up collision checking
        """
        self.game_name = game_name
        self.game_version = game_version
        self.window_width = window_width
        self.window_height = window_height
        self.game_speed = game_speed
        self.active_count = active_count
        self.sector_size = sector_size
        
class Grid:
    """
    Divide instances into sectors to improve collision detection speed.
    """
    def __init__(self, instances, width, height, sector_size):
        """
        ``width``, ``height`` and ``sector_size`` are all in pixels
        """
        self.width = width
        self.height = height
        self.sector_size = sector_size
        self.array = numpy.array([[set() for x in range(math.ceil(width/sector_size))] for y in range(math.ceil(height/sector_size))])
        for instance in instances:
            x = instance.x//sector_size
            y = instance.y//sector_size
            self.array[y, x].add(instance)
            
    def adjacent_cells(self, instance):
        """
        Return instances in cells that are adjacent to the one at ``x, y`` for the purposes of collision checking.
        Below, `o` is the cell at ``x, y``, and `#` represents the cells that will be returned::
        
          #
        o #
        # #
        This function also returns instances in the cell at ``x, y``.
        """
        x = instance.x//sector_size
        y = instance.y//sector_size
        result = set()
        for dy, dx in ((0, 0), (1, 0), (1, 1), (0, 1), (-1, 1)):
            try:
                result.update(self.array[y+dy, x+dx])
            except IndexError:
                pass
                
        return result
        
    def add(self, instance):
        """
        Add an instance to the grid.
        """
        self.array[instance.y//self.sector_size, instance.x//self.sector_size].add(instance)
        
    def remove(self, instance):
        """
        Remove an instance from the grid.
        """
        self.array[instance.y//self.sector_size, instance.x//self.sector_size].remove(instance)
    
    def move(self, instance, new_x, new_y):
        """
        Remove an instance from the cell at ``old_x, old_y``, and put it in a new one based on its position.
        """
        self.remove(instance)
        self.array[new_y//self.sector_size, new_x//self.sector_size].add(instance)
        
    def select_region(self, x, y, width, height):
        """
        Return all instances in cells within the rectangle defined by ``x``, ``y``, ``width``, and ``height.
        """
        left = max(int(x//self.sector_size), 0)
        top = max(int(y//self.sector_size), 0)
        right = left + (width//self.sector_size) + 1
        bottom = top + (height//self.sector_size) + 1
        return set.union(*[self.array[y, x] for y in range(top, bottom) for x in range(left, right)])
            
    def enumerate_cells(self):
        return numpy.ndenumerate(self.array)
