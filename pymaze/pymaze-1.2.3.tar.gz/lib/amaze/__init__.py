# coding=utf-8
# pymaze
# Copyright (C) 2012-2014 Moses Palmér
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.

import math
import os
import random
import re
import sys

try:
    import cairocffi as cairo
except ImportError:
    try:
        import cairo
    except ImportError:
        print('This program requires cairo')
        sys.exit(1)

from maze.quad import Maze
from maze.tri import TriMaze
from maze.hex import HexMaze
from maze.randomized_prim import initialize

from .terminal import print_maze
from .image import make_image


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description = 'A tool to generate mazes')

    def maze_size(s):
        result = int(s)
        if result < 1:
            raise argparse.ArgumentTypeError(
                'The maze size must be greater than 0')
        else:
            return result
    parser.add_argument('--maze-size', type = maze_size, nargs = 2,
        metavar = ('WIDTH', 'HEIGHT'),
        default = (15, 10),
        help = 'The size of the maze.')

    maze_classes = dict((len(mc.Wall.WALLS), mc) for mc in (
        Maze, TriMaze, HexMaze))
    parser.add_argument('--walls', type = int,
        choices = maze_classes.keys(),
        default = 4,
        help = 'The number of walls for every room.')

    def char(s):
        if len(s) != 1:
            raise argparse.ArgumentTypeError('%s is not a valid character' % s)
        else:
            return s
    parser.add_argument('--print-wall-char', type = char,
        default = '@',
        help = 'The character used for walls when printing the maze.')
    parser.add_argument('--print-path-char', type = char,
        default = '.',
        help = 'The character used for the path when printing the maze.')
    parser.add_argument('--print-floor-char', type = char,
        default = ' ',
        help = 'The character used for the floor when printing the maze.')

    def print_room_size(s):
        result = int(s)
        if result < 3:
            raise argparse.ArgumentTypeError(
                'The room size must be greater than or equal to 3')
        else:
            return result
    parser.add_argument('--print-room-size', type = print_room_size,
        nargs = 2,
        default = (5, 4),
        help = 'The size of each room in characters when printing the maze.')

    def image_room_size(s):
        result = int(s)
        if result < 1:
            raise argparse.ArgumentTypeError(
                'The maze room size in the image must be greater than 0')
        else:
            return int(0.5 * math.sqrt(2.0) * result)
    parser.add_argument('--image-room-size', type = image_room_size, nargs = 2,
        metavar = ('WIDTH', 'HEIGHT'),
        default = (30, 30),
        help = 'The size of the rooms in the maze image.')

    surface_types = {
        'pdf': (
            lambda f, w, h: cairo.PDFSurface(f, w, h),
            lambda f, surface: None),
        'png': (
            lambda f, w, h: cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h),
            lambda f, surface: surface.write_to_png(f)),
        'ps': (
            lambda f, w, h: cairo.PSSurface(f, w, h),
            lambda f, surface: None),
        'svg': (
            lambda f, w, h: cairo.SVGSurface(f, w, h),
            lambda f, surface: None)}
    def surface(s):
        try:
            ext = s.rsplit(os.path.extsep, 1)[1]
            return (
                lambda w, h: surface_types[ext][0](s, w, h),
                lambda surface: surface_types[ext][1](s, surface))
        except KeyError as e:
            argparse.ArgumentTypeError(
                '"%s" is not a valid file extension' % e.args[0])
        except IndexError:
            argparse.ArgumentTypeError(
                'The image file must have a valid extension')
    class default:
        def write(*args, **kwargs):
            pass
    parser.add_argument('--image-output', type = surface,
        metavar = 'FILENAME',
        required = True,
        help = ('The name of the image file to create. Valid types are %s.') % (
            ', '.join(surface_types.keys())))

    def color(allow_rgba):
        def rgb(s):
            result = None
            m = re.match(r'''(?x)
                \#(?P<red>[0-9A-Fa-f]{2})
                 (?P<green>[0-9A-Fa-f]{2})
                 (?P<blue>[0-9A-Fa-f]{2})''', s)
            if not m is None:
                result = tuple(float(int(d, 16)) / 255 for d in m.groups())
            else:
                m = re.match(r'''(?x)
                    rgb\(
                        \s*(?P<red>\d{1,3}%?)\s*,
                        \s*(?P<green>\d{1,3}%?)\s*,
                        \s*(?P<blue>\d{1,3}%?)\s*\)''', s)
                if not m is None:
                    result = tuple(float(d) / 255 if d[-1].isdigit()
                        else float(d[:-1]) / 100 for d in m.groups())
            if result is None or any(r < 0 or r > 1.0 for r in result):
                raise argparse.ArgumentTypeError(
                    '"%s" is not a valid colour.' % s)
            return result + (1.0,)
        def rgba(s):
            result = None
            m = re.match(r'''(?x)
                \#(?P<alpha>[0-9A-Fa-f]{2})
                 (?P<red>[0-9A-Fa-f]{2})
                 (?P<green>[0-9A-Fa-f]{2})
                 (?P<blue>[0-9A-Fa-f]{2})''', s)
            if not m is None:
                result = tuple(float(int(d, 16)) / 255
                    for d in m.groups()[1:] + (m.group(1),))
            else:
                m = re.match(r'''(?x)
                    rgba\(
                        \s*(?P<red>\d{1,3}%?)\s*,
                        \s*(?P<green>\d{1,3}%?)\s*,
                        \s*(?P<blue>\d{1,3}%?)\s*\,
                        \s*(?P<alpha>\d{1,3}%?)\s*\)''', s)
                if not m is None:
                    result = tuple(float(d) / 255 if d[-1].isdigit()
                        else float(d[:-1]) / 100 for d in m.groups())
            if result is None:
                return rgb(s)
            elif any(r < 0 or r > 1.0 for r in result):
                raise argparse.ArgumentTypeError(
                    '"%s" is not a valid colour.' % s)
            return result
        if allow_rgba:
            return rgba
        else:
            return rgb
    parser.add_argument('--image-background-color', type = color(True),
        metavar = 'COLOUR',
        default = (0.0, 0.0, 0.0),
        help = 'The background colour of the image. This must be specified as '
            'an HTML colour on the form #RRGGBB or rgb(r, g, b), or #AARRGGBB '
            'or rgba(r, g, b, a).')
    parser.add_argument('--image-wall-color', type = color(False),
        metavar = 'COLOUR',
        default = (1.0, 1.0, 1.0),
        help = 'The colour of the wall in the image. This must be specified as '
            'an HTML colour on the form #RRGGBB or rgb(r, g, b).')
    parser.add_argument('--image-path-color', type = color(True),
        metavar = 'COLOUR',
        default = (0.8, 0.4, 0.2),
        help = 'The colour of the path in the image. This must be specified as '
            'an HTML colour on the form #RRGGBB or rgb(r, g, b), or #AARRGGBB '
            'or rgba(r, g, b, a).')

    def line_width(s):
        result = int(s)
        if result < 2:
            raise argparse.ArgumentTypeError(
                'Line widths must be greater than 1')
        elif result & 1:
            raise argparse.ArgumentTypeError(
                'Line widths must be an even number')
        else:
            return result
    parser.add_argument('--image-wall-width', type = line_width,
        metavar = 'WIDTH',
        default = 2,
        help = 'The width of the maze wall lines.')
    parser.add_argument('--image-path-width', type = line_width,
        metavar = 'WIDTH',
        default = 2,
        help = 'The width of the maze path lines.')

    parser.add_argument('--image-path-smooth',
        action = 'store_true',
        default = False,
        help = 'Whether the path should be painted as a smooth curve instead '
            'of a sharp line.')

    namespace = parser.parse_args()

    # Create and initialise the maze
    maze = maze_classes[namespace.walls](*namespace.maze_size)
    initialize(maze, lambda max: random.randint(0, max - 1))
    solution = list(maze.walk_path((0, 0), (maze.width - 1, maze.height - 1)))

    print_maze(maze, solution, **dict(
            (name.split('_', 1)[1], value)
                for name, value in vars(namespace).items()
                if name.startswith('print_')))
    make_image(maze, solution, **dict(
            (name.split('_', 1)[1], value)
                for name, value in vars(namespace).items()
                if name.startswith('image_')))
