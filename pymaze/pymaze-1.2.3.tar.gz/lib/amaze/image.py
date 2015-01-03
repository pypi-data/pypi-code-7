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

try:
    import cairocffi as cairo
except ImportError:
    import cairo
import math
import sys


def calculate_bounds(maze):
    """Calculates the bounds of the walls of a maze.

    :param maze.BaseMaze maze: The maze whose bounds to calculate.

    :return: the tuple ``(min_x, min_y, max_x, max_y)``
    :rtype: (int, int)
    """
    class infinity(object):
        def __cmp__(self, other):
            if isinstance(other, type(self)): return 0
            else: return 1
    max_x, max_y = 0, 0
    min_x, min_y = infinity(), infinity()
    for wall in maze.edge_walls:
        a = wall.span[0]
        cx, cy = maze.get_center(wall.room_pos)
        px, py = cx + math.cos(a), cy + math.sin(a)
        max_x, max_y = max(max_x, px), max(max_y, py)
        min_x, min_y = min(min_x, px), min(min_y, py)
    return (min_x, min_y, max_x, max_y)

def draw_walls(maze, ctx, coords):
    """Draws the walls of a maze.

    :param maze.BaseMaze maze: The maze whose walls to draw.

    :param ctx: The cairo context to use for drawing.

    :param coords: A callable that transforms its parameters
        ``(maze_x, maze_y)`` to coordinates in the cairo context.
    """
    # Note that we have not yet painted any walls for any rooms
    for room_pos in maze.room_positions:
        maze[room_pos].painted = set()

    # Initialise the wall queue
    queue = []
    def extend_queue():
        """Finds a room with walls that have not yet been painted and adds them
        to queue.
        """
        for room_pos in maze.room_positions:
            remaining = [w
                for w in maze.walls(room_pos)
                if not int(w) in maze[w.room_pos]
                    and not int(w) in maze[w.room_pos].painted]
            if remaining:
                queue.extend(remaining)
                break
    extend_queue()

    # Draw the walls
    needs_move = True
    while queue:
        # Get the last wall from the queue and retrieve all remaining walls in
        # its corner; we add the back of the walls in order to actually move
        # along the wall instead of just spinning around the corner
        wall = queue.pop()
        walls = [w.back if w.back in maze else w
            for w in wall.corner_walls
            if w in maze or w.back in maze]
        remaining = [w for w in walls
            if not int(w) in maze[w.room_pos]
                and not int(w) in maze[w.room_pos].painted
                and not w == wall]

        # Queue all remaining walls for later use
        queue.extend(remaining)

        start_angle, end_angle = wall.span
        offset_x, offset_y = maze.get_center(wall.room_pos)

        def angle_to_coordinate(angle):
            """Converts an angle from a wall span in the current room to a
            coordinate.

            :param float angle: The angle to convert.

            :return: the tuple ``(x, y)``
            :rtype: (int, int)
            """
            return coords(
                offset_x + math.cos(angle),
                offset_y + math.sin(angle))

        # If we need to move, we move to the end of the span since
        # maze.Wall.from_corner will yield walls with the start span in the
        # given corner
        if needs_move:
            ctx.move_to(*angle_to_coordinate(end_angle))
        ctx.line_to(*angle_to_coordinate(start_angle))

        # Mark the current wall as painted, and the wall on the other side as
        # well as long as this is not a wall along the edge of the maze
        maze[wall.room_pos].painted.add(int(wall))
        if not maze.edge(wall):
            maze[wall.back.room_pos].painted.add(int(wall.back))

        # If we have reached a dead end, we need to stroke the line and start
        # over with a wall from the queue
        if not remaining:
            ctx.stroke()
            needs_move = True
        else:
            needs_move = False

        # If the queue is empty, check if any walls remain
        if not queue:
            extend_queue()

    ctx.stroke()

    # Remove the temporary attribute
    for room_pos in maze.room_positions:
        del maze[room_pos].painted

def draw_path_smooth(maze, ctx, coords, solution):
    """Draws the solution path using a smooth *bezier* curve.

    :param maze.BaseMaze maze: The maze whose solution to draw.

    :param ctx: The cairo context to use for drawing.

    :param coords: A callable that transforms its parameters
        ``(maze_x, maze_y)`` to coordinates in the cairo context.

    :param solution: The solution. This must be a list of all rooms to traverse.
    :type solution: [(int, int)]
    """
    room_positions = ((solution[i - 1], solution[i], solution[i + 1])
        for i in range(1, len(solution) - 1))
    ctx.move_to(*coords(*maze.get_center(solution[0])))
    for (previous_pos, current_pos, next_pos) in room_positions:
        # Draw a bezier curve from the wall to the previous room to the wall
        # to the next room
        previous_center = coords(*maze.get_center(previous_pos))
        current_center = coords(*maze.get_center(current_pos))
        next_center = coords(*maze.get_center(next_pos))
        d = 0.3
        ctx.curve_to(
            d * previous_center[0] + (1.0 - d) * current_center[0],
            d * previous_center[1] + (1.0 - d) * current_center[1],
            d * next_center[0] + (1.0 - d) * current_center[0],
            d * next_center[1] + (1.0 - d) * current_center[1],
            0.5 * (current_center[0] + next_center[0]),
            0.5 * (current_center[1] + next_center[1]))
    ctx.line_to(*coords(*maze.get_center(solution[-1])))
    ctx.stroke()

def draw_path(maze, ctx, coords, solution):
    """Draws the solution path using straight lines.

    :param maze.BaseMaze maze: The maze whose solution to draw.

    :param ctx: The cairo context to use for drawing.

    :param coords: A callable that transforms its parameters
        ``(maze_x, maze_y)`` to coordinates in the cairo context.

    :param solution: The solution. This must be a list of all rooms to traverse.
    :type solution: [(int int)]
    """
    for i, room_pos in enumerate(solution):
        # Draw a line to the centre of the room
        center = coords(*maze.get_center(room_pos))
        if i == 0:
            ctx.move_to(*center)
        else:
            ctx.line_to(*center)
    ctx.stroke()

def make_image(maze, solution, room_size, output, background_color, wall_color,
        path_color, wall_width, path_width, path_smooth):
    room_width, room_height = room_size
    image_create, image_write = output

    # Calculate the actual size of the image
    min_x, min_y, max_x, max_y = calculate_bounds(maze)

    # Create the cairo surface and context
    width = int((max_x - min_x) * room_width) + 2 * wall_width + 1
    height = int((max_y - min_y) * room_height) + 2 * wall_width + 1
    surface = image_create(width, height)
    ctx = cairo.Context(surface)

    # Make line caps and line joins round
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)

    # Clear the background
    ctx.set_source_rgba(*background_color)
    ctx.paint()

    def coords(x, y):
        """
        Converts coordinates from maze coordinates to context coordinates.

        The coordinates are scaled according to the room dimesions and offset
        with the minimum coordinates in the respective dimension and then
        rounded to make the lines sharp when drawing.

        @param x, y
            The maze coordinates to convert.
        @return coordinates to use for drawing
        """
        return (
            wall_width + (
                round((x - min_x) * room_width)),
            height - wall_width - (
                round((y - min_y) * room_height)))

    # Draw the walls
    ctx.set_source_rgba(*wall_color)
    ctx.set_line_width(wall_width)
    draw_walls(maze, ctx, coords)

    # Draw the path
    ctx.set_source_rgba(*path_color)
    ctx.set_line_width(path_width)
    if path_smooth:
        draw_path_smooth(maze, ctx, coords, solution)
    else:
        draw_path(maze, ctx, coords, solution)

    image_write(surface)

