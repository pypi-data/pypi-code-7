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


def initialize(maze, randomizer):
    """A function that initialises a maze with the randomised prim algorithm.

    See `here <http://en.wikipedia.org/wiki/Maze_generation_algorithm>`_.

    :param maze.BaseMaze maze: The maze to initialise.

    :param randomizer: The function used as a source of randomness. It will be
        called with an argument describing the maximum value to return. It may
        return any integers between ``0`` and the non-inclusive maximum value.
    """
    # Start with a random room and add all its walls except those on the edge
    start_x, start_y = randomizer(maze.width), randomizer(maze.height)
    walls = [wall for wall in maze.walls((start_x, start_y))
        if not maze.edge(wall)]

    while walls:
        # Select a random wall
        index = randomizer(len(walls))
        wall = walls.pop(index)

        # Get the room behind the wall
        next_room_pos = maze.walk(wall)

        # Is this the first time we visit this room?
        if not maze[next_room_pos]:
            # Add a door to the wall
            maze.set_door(wall.room_pos, wall, True)

            # Add all walls of the new room except those leading to rooms
            # already visited or leading out of the maze
            for w in maze.walls(next_room_pos):
                try:
                    if not maze[maze.walk(w)]:
                        walls.append(w)
                except IndexError:
                    pass
