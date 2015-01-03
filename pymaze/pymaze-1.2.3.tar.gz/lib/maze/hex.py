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

from . import BaseWall, BaseMaze


class HexWall(BaseMaze.Wall):
    # The angles for each corner; this is a list of the tuple (angle, alt_angle)
    # where alt_angle is used for the room at x, y when x + y is odd
    _ANGLES = []

    # The directions for each wall; this is a list of the tuple (dir, alt_dir)
    # where alt_dir is used for the room at x, y when x + y is odd
    _DIRECTIONS = []

    # The names of the walls
    NAMES = []

    # The list of walls; this is the list [0, 1, 2... N]
    WALLS = []

    # The horizontal scale factor when converting maze coordinates to physical
    # coordinates
    HORIZONTAL_MULTIPLICATOR = 2.0 * math.cos(math.pi / 6)

    # The vertical scale factor when converting maze coordinates to physical
    # coordinates
    VERTICAL_MULTIPLICATOR = 2.0 - math.sin(math.pi / 6)

    __slots__ = tuple()

    start_angle = math.pi / 2 + (2 * 2 * math.pi) / 6
    data = (
        ('LEFT', (-1, 0), None),
        ('UP_LEFT', (-1, 1), (0, 1)),
        ('UP_RIGHT', (0, 1), (1, 1)),
        ('RIGHT', (1, 0), None),
        ('DOWN_RIGHT', (0, -1), (1, -1)),
        ('DOWN_LEFT', (-1, -1), (0, -1)))
    for i, (name, dir1, dir2) in enumerate(data):
        locals()[name] = i

        next_angle = _ANGLES[-1] - 2 * math.pi / len(data) \
            if _ANGLES else start_angle
        while next_angle < 0.0:
            next_angle += 2 * math.pi
        _ANGLES.append(next_angle)

        _DIRECTIONS.append((dir1, dir2))

        NAMES.append(name.lower())
        WALLS.append(i)

    @classmethod
    def from_direction(self, room_pos, direction):
        """
        @see Maze.Wall.from_direction
        """
        use_alt = room_pos[1] % 2 == 1
        for i, (dir1, dir2) in enumerate(self._DIRECTIONS):
            if direction == (dir1 if not use_alt or not dir2 else dir2):
                return self(room_pos, i)

        raise ValueError('Invalid direction for %s: %s' % (
            str(room_pos), str(direction)))

    def _get_direction(self):
        """
        @see Maze.Wall._get_direction
        """
        if (self.room_pos[1] % 2 == 1) and self._DIRECTIONS[self.wall][1]:
            return self._DIRECTIONS[self.wall][1]
        else:
            return self._DIRECTIONS[self.wall][0]

class HexMaze(BaseMaze):
    """A maze with hexagonal rooms.

    The rooms are laid out in rows, where every odd row is moved a half room in
    the positive horizontal direction; the appearance of the maze is that of a
    honey comb.
    """
    Wall = HexWall

    def get_center(self, room_pos):
        return (
            (room_pos[0] + (1.0 if room_pos[1] % 2 == 1 else 0.5))
                * self.Wall.HORIZONTAL_MULTIPLICATOR,
            (room_pos[1] + 0.5) * self.Wall.VERTICAL_MULTIPLICATOR)
