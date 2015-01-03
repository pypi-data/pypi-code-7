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


class TriWall(BaseMaze.Wall):
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
    HORIZONTAL_MULTIPLICATOR = math.cos(math.pi / 2 + 2 * 2 * math.pi / 3)

    # The vertical scale factor when converting maze coordinates to physical
    # coordinates
    VERTICAL_MULTIPLICATOR = 2 + math.sin(math.pi / 2 + 2 * math.pi / 3)

    # The vertical offset added or removed when converting maze coordinates to
    # physical coordinates; it is added if x + y is odd
    OFFSET = 0.5 * (1 + math.sin(math.pi / 2 + 2 * math.pi / 3))

    __slots__ = tuple()

    start_angle = math.pi / 2 + 2 * math.pi / 3
    data = (
        ('DIAGONAL_1', (-1, 0), (1, 0)),
        ('DIAGONAL_2', (1, 0), (-1, 0)),
        ('HORIZONTAL', (0, -1), (0, 1)))
    for i, (name, dir1, dir2) in enumerate(data):
        locals()[name] = i

        next_angle = _ANGLES[-1][0] - 2 * math.pi / len(data) \
            if _ANGLES else start_angle
        while next_angle < 0.0:
            next_angle += 2 * math.pi
        alt_angle = next_angle - math.pi
        while alt_angle < 0.0:
            alt_angle += 2 * math.pi
        _ANGLES.append((next_angle, alt_angle))

        _DIRECTIONS.append((dir1, dir2))

        NAMES.append(name.lower())
        WALLS.append(i)

    @classmethod
    def from_direction(self, room_pos, direction):
        """
        @see Maze.Wall.from_direction
        """
        alt = (room_pos[0] + room_pos[1]) % 2
        for i, dirs in enumerate(self._DIRECTIONS):
            if direction == dirs[alt]:
                return self(room_pos, i)

        raise ValueError('Invalid direction for %s: %s' % (
            str(room_pos), str(direction)))

    @classmethod
    def from_corner(self, room_pos, wall_index):
        """
        @see Maze.Wall.from_corner
        """
        start_wall = wall = self(room_pos, wall_index)

        while True:
            yield wall

            back = wall.back
            next_room_pos = back.room_pos
            next_wall = (int(back) + 1) % len(self.WALLS)
            next = self(next_room_pos, next_wall)
            if next == start_wall:
                break

            wall = next

    def _get_opposite_index(self):
        """
        There is no opposite wall in a triangular room.

        @raise NotImplementedError
        """
        raise NotImplementedError()

    def _get_back_index(self):
        """
        @see Maze.Wall._get_back_index
        """
        return self.wall

    def _get_direction(self):
        """
        @see Maze.Wall._get_direction
        """
        alt = (self.room_pos[0] + self.room_pos[1]) % 2
        return self._DIRECTIONS[self.wall][alt]

    def _get_span(self):
        """
        @see Maze.Wall._get_span
        """
        alt = (self.room_pos[0] + self.room_pos[1]) % 2
        start = self._ANGLES[self.wall][alt]
        end = self._ANGLES[(self.wall + 1) % len(self._ANGLES)][alt]

        return (start, end)

class TriMaze(BaseMaze):
    """A maze with triangular rooms.

    The rooms alternate between having a wall facing downwards and a corner
    facing downwards. The room at x, y will have a corner facing downwards if
    x + y is odd.

    Walls in a triangular maze do not have an opposite wall.
    """
    Wall = TriWall

    def get_center(self, room_pos):
        alt = (room_pos[0] + room_pos[1]) % 2
        sign = 1 if alt == 1 else -1
        return (
            (room_pos[0] + 0.5) * self.Wall.HORIZONTAL_MULTIPLICATOR,
            (room_pos[1] + 0.5) * self.Wall.VERTICAL_MULTIPLICATOR \
                + sign * self.Wall.OFFSET)
