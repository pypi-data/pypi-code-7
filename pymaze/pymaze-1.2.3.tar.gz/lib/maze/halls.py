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


def initialize(maze, randomizer, attempts = 20, max_width = None,
    max_height = None):
    """A function that initialises a maze with a number of larger rooms, halls.

    A number of attempts to generate overlapping rooms in the maze are made. If
    the larger room is fully inside the maze, and all rooms from which it is
    created are non-flagged, the walls of all rooms, except walls leading out of
    the larger room, will be removed, and the rooms will be flagged.

    :param maze.BaseMaze maze: The maze to initialise.

    :param randomizer: The function used as a source of randomness. It will be
        called with an argument describing the maximum value to return. It may
        return any integers between ``0`` and the non-inclusive maximum value.

    :param int attempts: The number of attempts to make.

    :param max_width: The maximum width of a room, or None to use the default of
        one third of the maze width. Passing ``0`` for this value is the same as
        passing ``None``.
    :type max_width: int or None

    :param max_height: The maximum height of a room, or None to use the default
        of one third of the maze height. Passing ``0`` for this value is the
        same as passing ``None``.
    :type max_height: int or None

    :return: a data structure usable by :func:`finalize`
    """
    max_width = max_width or maze.width // 3
    max_height = max_height or maze.height // 3

    def rooms(x, y, width, height):
        """Yields all rooms in the given hall.
        """
        for i in range(width):
            for j in range(height):
                room_pos = (x + i, y + j)
                if room_pos in maze:
                    yield room_pos

    def walls(x, y, width, height):
        """Returns all walls surrounding a hall.
        """
        def inside(wall):
            if wall.room_pos[0] < x or wall.room_pos[0] >= x + width:
                return False
            if wall.room_pos[1] < y or wall.room_pos[1] >= y + height:
                return False
            return True

        result = []
        for i in range(width - 2): # Top
            result.extend(wall
                for wall in maze.walls((x + 1 + i, y))
                if not inside(wall.back))
        for i in range(height - 2): # Right
            result.extend(wall
                for wall in maze.walls((x + width - 1, y + 1 + i))
                if not inside(wall.back))
        for i in range(width - 2): # Bottom
            result.extend(wall
                for wall in maze.walls((x + 1 + width - 1 - i, y + height - 1))
                if not inside(wall.back))
        for i in range(height - 2): # Left
            result.extend(wall
                for wall in maze.walls((x, y + 1 + height - 1 - i))
                if not inside(wall.back))
        return result

    while attempts:
        attempts -= 1

        # Randomize the room
        width = randomizer(maze.width // 3) + 1
        height = randomizer(maze.height // 3) + 1
        x = randomizer(maze.width - width)
        y = randomizer(maze.height - height)

        # If any room inside the large room is not unknown, do nothing; keep a
        # one-room margin
        if any(not maze[room_pos].unknown
                for room_pos in rooms(x - 1, y - 1, width + 2, height + 2)):
            continue

        # Open all internal walls of the hall
        for room_pos in rooms(x, y, width, height):
            for w in maze.walls(room_pos):
                back_room_pos = w.back.room_pos
                if back_room_pos[0] < x or back_room_pos[0] >= x + width:
                    continue
                if back_room_pos[1] < y or back_room_pos[1] >= y + height:
                    continue
                maze.set_door(room_pos, w, True)
            maze[room_pos].flagged = True

        # Open up some of the external walls of the hall
        hall_walls = walls(x, y, width, height)
        for wall in hall_walls:
            if not wall.back in maze:
                continue
            if randomizer(len(hall_walls)) < 4:
                maze.set_door(wall.room_pos, wall, True)
