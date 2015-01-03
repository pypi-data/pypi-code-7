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


class QuadWall(BaseWall):
    # The angles for each corner
    _ANGLES = []

    # The directions for each wall
    _DIRECTIONS = []

    # The names of the walls
    NAMES = []

    # The list of walls; this is the list [0, 1, 2... N]
    WALLS = []

    # The scale factor when converting maze coordinates to physical coordinates
    MULTIPLICATOR = 2.0 / math.sqrt(2.0)

    __slots__ = tuple()

    start_angle = (5 * math.pi) / 4
    data = (
        ('LEFT', (-1, 0)),
        ('UP', (0, 1)),
        ('RIGHT', (1, 0)),
        ('DOWN', (0, -1)))
    for i, (name, dir1) in enumerate(data):
        locals()[name] = i

        next_angle = _ANGLES[-1] - 2 * math.pi / len(data) \
            if _ANGLES else start_angle
        while next_angle < 0.0:
            next_angle += 2 * math.pi
        _ANGLES.append(next_angle)

        _DIRECTIONS.append(dir1)

        NAMES.append(name.lower())
        WALLS.append(i)

class Maze(BaseMaze):
    """A maze with square rooms.

    This is the traditional maze. Maze coordinates correspond to physical
    coordinates after a simple scale operation.
    """
    Wall = QuadWall

    def get_center(self, room_pos):
        return (
            (room_pos[0] + 0.5) * self.Wall.MULTIPLICATOR,
            (room_pos[1] + 0.5) * self.Wall.MULTIPLICATOR)
