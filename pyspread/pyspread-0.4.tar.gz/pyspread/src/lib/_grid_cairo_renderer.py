#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright Martin Manns
# Distributed under the terms of the GNU General Public License

# --------------------------------------------------------------------
# pyspread is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyspread is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyspread.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------

"""
_grid_cairo_renderer.py
=======================

Provides
--------

 * GridCairoRenderer: Renders grid slice to Cairo context
 * GridCellCairoRenderer: Renders grid cell to Cairo context
 * GridCellContentCairoRenderer: Renders cell content to Cairo context
 * GridCellBackgroundCairoRenderer: Renders cell background to Cairo context
 * GridCellBorderCairoRenderer: Renders cell border to Cairo context

"""

import math
import sys
import warnings

import cairo
import wx
import wx.lib.wxcairo


try:
    import matplotlib.pyplot as pyplot
    from matplotlib.backends.backend_cairo import RendererCairo
    from matplotlib.backends.backend_cairo import FigureCanvasCairo
    from matplotlib.transforms import Affine2D
except ImportError:
    pyplot = None

import pango
import pangocairo

from src.lib.parsers import color_pack2rgb, is_svg


STANDARD_ROW_HEIGHT = 20
STANDARD_COL_WIDTH = 50

try:
    from src.config import config
    MAX_RESULT_LENGTH = config["max_result_length"]
except ImportError:
    MAX_RESULT_LENGTH = 100000


class GridCairoRenderer(object):
    """Renders a grid slice to a CairoSurface

    Parameters
    ----------

    * context: pycairo.context
    \tThe Cairo context to be drawn to
    * code_array: model.code_array
    \tGrid data structure that yields rendering information
    * row_tb: 2 tuple of Integer
    \tStart and stop of row range with step 1
    * col_lr: 2 tuple of Integer
    \tStart and stop of col range with step 1
    * tab_fl: 2 tuple of Integer
    \tStart and stop of tab range with step 1
    * width: Float
    \tPage width in points
    * height: Float
    \tPage height in points
    * orientation: String in ["portrait", "landscape"]
    \tPage orientation
    * x_offset: Float, defaults to 20.5
    \t X offset from bage border in points
    * y_offset: Float, defaults to 20.5
    \t Y offset from bage border in points

    """

    def __init__(self, context, code_array, row_tb, col_rl, tab_fl,
                 width, height, orientation, x_offset=20.5, y_offset=20.5):
        self.context = context
        self.code_array = code_array

        self.row_tb = row_tb
        self.col_rl = col_rl
        self.tab_fl = tab_fl

        self.width = width
        self.height = height

        self.x_offset = x_offset
        self.y_offset = y_offset

        self.orientation = orientation

    def get_cell_rect(self, row, col, tab):
        """Returns rectangle of cell on canvas"""

        top_row = self.row_tb[0]
        left_col = self.col_rl[0]

        pos_x = self.x_offset
        pos_y = self.y_offset

        merge_area = self._get_merge_area((row, col, tab))

        for __row in xrange(top_row, row):
            __row_height = self.code_array.get_row_height(__row, tab)
            pos_y += __row_height

        for __col in xrange(left_col, col):
            __col_width = self.code_array.get_col_width(__col, tab)
            pos_x += __col_width

        if merge_area is None:
            height = self.code_array.get_row_height(row, tab)
            width = self.code_array.get_col_width(col, tab)
        else:
            # We have a merged cell
            top, left, bottom, right = merge_area
            # Are we drawing the top left cell?
            if top == row and left == col:
                # Set rect to merge area
                heights = (self.code_array.get_row_height(__row, tab)
                           for __row in xrange(top, bottom+1))
                widths = (self.code_array.get_col_width(__col, tab)
                          for __col in xrange(left, right+1))
                height = sum(heights)
                width = sum(widths)
            else:
                # Do not draw the cell because it is hidden
                return

        return pos_x, pos_y, width, height

    def _get_merge_area(self, key):
        """Returns the merge area of a merged cell

        Merge area is a 4 tuple (top, left, bottom, right)

        """

        cell_attributes = self.code_array.cell_attributes[key]
        return cell_attributes["merge_area"]

    def draw(self):
        """Draws slice to context"""

        row_start, row_stop = self.row_tb
        col_start, col_stop = self.col_rl
        tab_start, tab_stop = self.tab_fl

        for tab in xrange(tab_start, tab_stop):
            # Scale context to page extent
            # In order to keep the aspect ration intact use the maximum
            first_key = row_start, col_start, tab
            first_rect = self.get_cell_rect(*first_key)

            # If we have a merged cell then use the top left cell rect
            if first_rect is None:
                top, left, __, __ = self._get_merge_area(first_key)
                first_rect = self.get_cell_rect(top, left, tab)

            last_key = row_stop - 1, col_stop - 1, tab
            last_rect = self.get_cell_rect(*last_key)

            # If we have a merged cell then use the top left cell rect
            if last_rect is None:
                top, left, __, __ = self._get_merge_area(last_key)
                last_rect = self.get_cell_rect(top, left, tab)

            x_extent = last_rect[0] + last_rect[2] - first_rect[0]
            y_extent = last_rect[1] + last_rect[3] - first_rect[1]

            scale_x = (self.width - 2 * self.x_offset) / float(x_extent)
            scale_y = (self.height - 2 * self.y_offset) / float(y_extent)

            self.context.save()
            # Translate offset to o
            self.context.translate(first_rect[0], first_rect[1])

            # Scale to fit page, do not change aspect ratio
            scale = min(scale_x, scale_y)
            self.context.scale(scale, scale)

            # Translate offset
            self.context.translate(-self.x_offset, -self.y_offset)

            # TODO: Center the grid on the page

            # Render cells

            for row in xrange(row_start, row_stop):
                for col in xrange(col_start, col_stop):
                    key = row, col, tab
                    rect = self.get_cell_rect(row, col, tab)  # Rect
                    if rect is not None:
                        cell_renderer = GridCellCairoRenderer(
                            self.context,
                            self.code_array,
                            key,  # (row, col, tab)
                            rect
                        )

                        cell_renderer.draw()

            # Undo scaling, translation, ...
            self.context.restore()

            self.context.show_page()


class GridCellCairoRenderer(object):
    """Renders a grid cell to a CairoSurface

    Parameters
    ----------

    * context: pycairo.context
    \tThe Cairo context to be drawn to
    * code_array: model.code_array
    \tGrid data structure that yields rendering information
    * key: 3 tuple of Integer
    \tKey of cell to be rendered
    * rect: 4 tuple of float
    \tx, y, width and height of cell rectangle

    """

    def __init__(self, context, code_array, key, rect):
        self.context = context
        self.code_array = code_array
        self.key = key
        self.rect = rect

    def draw(self):
        """Draws cell to context"""

        cell_background_renderer = GridCellBackgroundCairoRenderer(
            self.context,
            self.code_array,
            self.key,
            self.rect)

        cell_content_renderer = GridCellContentCairoRenderer(
            self.context,
            self.code_array,
            self.key,
            self.rect)

        cell_border_renderer = GridCellBorderCairoRenderer(
            self.context,
            self.code_array,
            self.key,
            self.rect)

        cell_background_renderer.draw()
        cell_content_renderer.draw()
        cell_border_renderer.draw()


class GridCellContentCairoRenderer(object):
    """Renders cell content to Cairo context

    Parameters
    ----------

    * context: pycairo.context
    \tThe Cairo context to be drawn to
    * code_array: model.code_array
    \tGrid data structure that yields rendering information
    * key: 3 tuple of Integer
    \tKey of cell to be rendered

    """

    def __init__(self, context, code_array, key, rect):
        self.context = context
        self.code_array = code_array
        self.key = key
        self.rect = rect

    def get_cell_content(self):
        """Returns cell content"""

        try:
            if self.code_array.cell_attributes[self.key]["button_cell"]:
                return

        except IndexError:
            return

        try:
            return self.code_array[self.key]

        except IndexError:
            pass

    def draw_bitmap(self, content):
        """Draws bitmap cell content to context"""

        # Get

        if content.HasAlpha():
            image = wx.ImageFromBitmap(content)
            image.ConvertAlphaToMask()
            image.SetMask(False)
            content = wx.BitmapFromImage(image)

        ims = wx.lib.wxcairo.ImageSurfaceFromBitmap(content)
        ims_width = ims.get_width()
        ims_height = ims.get_height()

        scale_x = self.rect[2] / float(ims_width)
        scale_y = self.rect[3] / float(ims_height)

        scale_x = min(scale_x, scale_y)
        scale_y = scale_x

        self.context.save()
        self.context.translate(-2, -2)  # Otherwise there is a white border
        self.context.scale(scale_x, scale_y)
        self.context.set_source_surface(ims, 0, 0)
        self.context.paint()
        self.context.restore()

    def draw_svg(self, svg_str):
        """Draws svg string to cell"""

        try:
            import rsvg
        except ImportError:
            self.draw_text(svg_str)
            return

        svg = rsvg.Handle(data=svg_str)

        dim = svg.get_dimension_data()
        scale_x = self.rect[2] / float(dim[0] + 10)  # Avoid cut offs
        scale_y = self.rect[3] / float(dim[1] + 5)
        scale_x = min(scale_x, scale_y)
        scale_y = scale_x
        self.context.save()
        self.context.scale(scale_x, scale_y)
        svg.render_cairo(self.context)
        self.context.restore()

    def draw_matplotlib_figure(self, figure):
        """Draws matplotlib figure to context"""

        class CustomRendererCairo(RendererCairo):
            """Workaround for older versins with limited draw path length"""

            if sys.byteorder == 'little':
                BYTE_FORMAT = 0  # BGRA
            else:
                BYTE_FORMAT = 1  # ARGB

            def draw_path(self, gc, path, transform, rgbFace=None):
                ctx = gc.ctx
                transform = transform + Affine2D().scale(1.0, -1.0).\
                    translate(0, self.height)
                ctx.new_path()
                self.convert_path(ctx, path, transform)
                self._fill_and_stroke(ctx, rgbFace, gc.get_alpha(),
                                      gc.get_forced_alpha())

            def draw_image(self, gc, x, y, im):
                # bbox - not currently used
                rows, cols, buf = im.color_conv(self.BYTE_FORMAT)
                surface = cairo.ImageSurface.create_for_data(
                    buf, cairo.FORMAT_ARGB32, cols, rows, cols*4)
                ctx = gc.ctx
                y = self.height - y - rows
                ctx.save()
                ctx.set_source_surface(surface, x, y)
                if gc.get_alpha() != 1.0:
                    ctx.paint_with_alpha(gc.get_alpha())
                else:
                    ctx.paint()
                ctx.restore()

        if pyplot is None:
            # Matplotlib is not installed
            return

        FigureCanvasCairo(figure)

        dpi = float(figure.dpi)

        # Set a border so that the figure is not cut off at the cell border
        border_x = 200 / (self.rect[2] / dpi) ** 2
        border_y = 200 / (self.rect[3] / dpi) ** 2

        width = (self.rect[2] - 2 * border_x) / dpi
        height = (self.rect[3] - 2 * border_y) / dpi

        figure.set_figwidth(width)
        figure.set_figheight(height)

        renderer = CustomRendererCairo(dpi)
        renderer.set_width_height(width, height)

        renderer.gc.ctx = self.context
        renderer.text_ctx = self.context

        self.context.save()
        self.context.translate(border_x, border_y + height * dpi)

        figure.draw(renderer)

        self.context.restore()

    def _get_text_color(self):
        """Returns text color rgb tuple of right line"""

        color = self.code_array.cell_attributes[self.key]["textcolor"]
        return tuple(c / 255.0 for c in color_pack2rgb(color))

    def set_font(self, pango_layout):
        """Sets the font for draw_text"""

        wx2pango_weights = {
            wx.FONTWEIGHT_BOLD: pango.WEIGHT_BOLD,
            wx.FONTWEIGHT_LIGHT: pango.WEIGHT_LIGHT,
            wx.FONTWEIGHT_NORMAL: pango.WEIGHT_NORMAL,
        }

        wx2pango_styles = {
            wx.FONTSTYLE_NORMAL: pango.STYLE_NORMAL,
            wx.FONTSTYLE_SLANT: pango.STYLE_OBLIQUE,
            wx.FONTSTYLE_ITALIC: pango.STYLE_ITALIC,
        }

        cell_attributes = self.code_array.cell_attributes[self.key]

        # Text font attributes
        textfont = cell_attributes["textfont"]
        pointsize = cell_attributes["pointsize"]
        fontweight = cell_attributes["fontweight"]
        fontstyle = cell_attributes["fontstyle"]
        underline = cell_attributes["underline"]
        strikethrough = cell_attributes["strikethrough"]

        # Now construct the pango font
        font_description = pango.FontDescription(
            " ".join([textfont, str(pointsize)]))
        pango_layout.set_font_description(font_description)

        attrs = pango.AttrList()

        # Underline
        attrs.insert(pango.AttrUnderline(underline, 0, MAX_RESULT_LENGTH))

        # Weight
        weight = wx2pango_weights[fontweight]
        attrs.insert(pango.AttrWeight(weight, 0, MAX_RESULT_LENGTH))

        # Style
        style = wx2pango_styles[fontstyle]
        attrs.insert(pango.AttrStyle(style, 0, MAX_RESULT_LENGTH))

        # Strikethrough
        attrs.insert(pango.AttrStrikethrough(strikethrough, 0,
                                             MAX_RESULT_LENGTH))

        pango_layout.set_attributes(attrs)

    def _rotate_cell(self, angle, rect, back=False):
        """Rotates and translates cell if angle in [90, -90, 180]"""

        if angle == 90 and not back:
            self.context.rotate(-math.pi / 2.0)
            self.context.translate(-rect[2] + 4, 0)

        elif angle == 90 and back:
            self.context.translate(rect[2] - 4, 0)
            self.context.rotate(math.pi / 2.0)

        elif angle == -90 and not back:
            self.context.rotate(math.pi / 2.0)
            self.context.translate(0, -rect[3] + 2)

        elif angle == -90 and back:
            self.context.translate(0, rect[3] - 2)
            self.context.rotate(-math.pi / 2.0)

        elif angle == 180 and not back:
            self.context.rotate(math.pi)
            self.context.translate(-rect[2] + 4, -rect[3] + 2)

        elif angle == 180 and back:
            self.context.translate(rect[2] - 4, rect[3] - 2)
            self.context.rotate(-math.pi)

    def draw_text(self, content):
        """Draws text cell content to context"""

        wx2pango_alignment = {
            "left": pango.ALIGN_LEFT,
            "center": pango.ALIGN_CENTER,
            "right": pango.ALIGN_RIGHT,
        }

        cell_attributes = self.code_array.cell_attributes[self.key]

        angle = cell_attributes["angle"]

        if angle in [-90, 90]:
            rect = self.rect[1], self.rect[0], self.rect[3], self.rect[2]
        else:
            rect = self.rect

        # Text color attributes
        self.context.set_source_rgb(*self._get_text_color())

        ptx = pangocairo.CairoContext(self.context)
        pango_layout = ptx.create_layout()
        self.set_font(pango_layout)

        pango_layout.set_wrap(pango.WRAP_WORD_CHAR)

        pango_layout.set_width(int(round((rect[2] - 4.0) * pango.SCALE)))

        try:
            markup = cell_attributes["markup"]
        except KeyError:
            # Old file
            markup = False

        if markup:
            with warnings.catch_warnings(record=True) as warning_lines:
                warnings.resetwarnings()
                warnings.simplefilter("always")
                pango_layout.set_markup(unicode(content))

                if warning_lines:
                    w2unicode = lambda m: unicode(m.message)
                    msg = u"\n".join(map(w2unicode, warning_lines))
                    pango_layout.set_text(msg)
        else:
            pango_layout.set_text(unicode(content))

        alignment = cell_attributes["justification"]
        pango_layout.set_alignment(wx2pango_alignment[alignment])

        # Shift text for vertical alignment
        extents = pango_layout.get_pixel_extents()

        downshift = 0

        if cell_attributes["vertical_align"] == "bottom":
            downshift = rect[3] - extents[1][3] - 4

        elif cell_attributes["vertical_align"] == "middle":
            downshift = int((rect[3] - extents[1][3]) / 2) - 2

        self._rotate_cell(angle, rect)
        self.context.translate(0, downshift)

        ptx.update_layout(pango_layout)
        ptx.show_layout(pango_layout)

        self.context.translate(0, -downshift)
        self._rotate_cell(angle, rect, back=True)

    def draw_roundedrect(self, x, y, w, h, r=10):
        """Draws a rounded rectangle"""
        # A****BQ
        # H     C
        # *     *
        # G     D
        # F****E

        context = self.context

        context.save

        context.move_to(x+r, y)  # Move to A
        context.line_to(x+w-r, y)  # Straight line to B
        context.curve_to(x+w, y, x+w, y, x+w, y+r)  # Curve to C
        # Control points are both at Q
        context.line_to(x+w, y+h-r)  # Move to D
        context.curve_to(x+w, y+h, x+w, y+h, x+w-r, y+h)  # Curve to E
        context.line_to(x+r, y+h)  # Line to F
        context.curve_to(x, y+h, x, y+h, x, y+h-r)  # Curve to G
        context.line_to(x, y+r)  # Line to H
        context.curve_to(x, y, x, y, x+r, y)  # Curve to A

        context.restore

    def draw_button(self, x, y, w, h, label):
        """Draws a button"""

        context = self.context

        self.draw_roundedrect(x, y, w, h)
        context.clip()

        # Set up the gradients
        gradient = cairo.LinearGradient(0, 0, 0, 1)
        gradient.add_color_stop_rgba(0, 0.5, 0.5, 0.5, 0.1)
        gradient.add_color_stop_rgba(1, 0.8, 0.8, 0.8, 0.9)
#        # Transform the coordinates so the width and height are both 1
#        # We save the current settings and restore them afterward
        context.save()
        context.scale(w, h)
        context.rectangle(0, 0, 1, 1)
        context.set_source_rgb(0, 0, 1)
        context.set_source(gradient)
        context.fill()
        context.restore()

        # Draw the button text
        # Center the text
        x_bearing, y_bearing, width, height, x_advance, y_advance = \
            context.text_extents(label)

        text_x = (w / 2.0)-(width / 2.0 + x_bearing)
        text_y = (h / 2.0)-(height / 2.0 + y_bearing) + 1

        # Draw the button text
        context.move_to(text_x, text_y)
        context.set_source_rgba(0, 0, 0, 1)
        context.show_text(label)

        # Draw the border of the button
        context.move_to(x, y)
        context.set_source_rgba(0, 0, 0, 1)
        self.draw_roundedrect(x, y, w, h)
        context.stroke()

    def draw(self):
        """Draws cell content to context"""

        # Content is only rendered within rect
        self.context.save()
        self.context.rectangle(*self.rect)
        self.context.clip()

        content = self.get_cell_content()

        pos_x, pos_y = self.rect[:2]
        self.context.translate(pos_x + 2, pos_y + 2)

        if self.code_array.cell_attributes[self.key]["button_cell"]:
            # Render a button instead of the cell
            label = self.code_array.cell_attributes[self.key]["button_cell"]
            self.draw_button(1, 1, self.rect[2]-5, self.rect[3]-5, label)

        elif isinstance(content, wx._gdi.Bitmap):
            # A bitmap is returned --> Draw it!
            self.draw_bitmap(content)

        elif pyplot is not None and isinstance(content, pyplot.Figure):
            # A matplotlib figure is returned --> Draw it!
            self.draw_matplotlib_figure(content)

        elif isinstance(content, basestring) and is_svg(content):
            # The content
            self.draw_svg(content)

        elif content is not None:
            self.draw_text(content)

        self.context.translate(-pos_x - 2, -pos_y - 2)

        # Remove clipping to rect
        self.context.restore()


class GridCellBackgroundCairoRenderer(object):
    """Renders cell background to Cairo context

    Parameters
    ----------

    * context: pycairo.context
    \tThe Cairo context to be drawn to
    * code_array: model.code_array
    \tGrid data structure that yields rendering information
    * key: 3 tuple of Integer
    \tKey of cell to be rendered

    """

    def __init__(self, context, code_array, key, rect):
        self.context = context
        self.cell_attributes = code_array.cell_attributes
        self.key = key
        self.rect = rect

    def _get_background_color(self):
        """Returns background color rgb tuple of right line"""

        color = self.cell_attributes[self.key]["bgcolor"]
        return tuple(c / 255.0 for c in color_pack2rgb(color))

    def draw(self):
        """Draws cell background to context"""

        self.context.set_source_rgb(*self._get_background_color())
        self.context.rectangle(*self.rect)
        self.context.fill()


class GridCellBorderCairoRenderer(object):
    """Renders cell border to Cairo context

    Parameters
    ----------

    * context: pycairo.context
    \tThe Cairo context to be drawn to
    * code_array: model.code_array
    \tGrid data structure that yields rendering information
    * key: 3 tuple of Integer
    \tKey of cell to be rendered

    """

    def __init__(self, context, code_array, key, rect):
        self.context = context
        self.code_array = code_array
        self.cell_attributes = code_array.cell_attributes
        self.key = key
        self.rect = rect

    # Coordinates
    # -----------

    def _get_top_line_coordinates(self):
        """Returns start and stop coordinates of bottom line"""

        rect_x, rect_y, rect_width, _ = self.rect

        start_point = rect_x, rect_y
        end_point = rect_x + rect_width, rect_y

        return start_point, end_point

    def _get_bottom_line_coordinates(self):
        """Returns start and stop coordinates of bottom line"""

        rect_x, rect_y, rect_width, rect_height = self.rect

        start_point = rect_x, rect_y + rect_height
        end_point = rect_x + rect_width, rect_y + rect_height

        return start_point, end_point

    def _get_left_line_coordinates(self):
        """Returns start and stop coordinates of right line"""

        rect_x, rect_y, _, rect_height = self.rect

        start_point = rect_x, rect_y
        end_point = rect_x, rect_y + rect_height

        return start_point, end_point

    def _get_right_line_coordinates(self):
        """Returns start and stop coordinates of right line"""

        rect_x, rect_y, rect_width, rect_height = self.rect

        start_point = rect_x + rect_width, rect_y
        end_point = rect_x + rect_width, rect_y + rect_height

        return start_point, end_point

    def _get_topleft_right_line_coordinates(self):
        """Returns start and stop coordinates of top left cell's right line"""

        rect_x, rect_y, _, _ = self.rect

        start_point = rect_x, rect_y - 0.01
        end_point = rect_x, rect_y

        return start_point, end_point

    def _get_topleft_bottom_line_coordinates(self):
        """Returns start and stop coordinates of top left cell's bottom line"""

        rect_x, rect_y, _, _ = self.rect

        start_point = rect_x - 0.01, rect_y
        end_point = rect_x, rect_y

        return start_point, end_point

    # Colors
    # ------

    def _get_top_line_color(self):
        """Returns color rgb tuple of top line"""

        row, col, tab = self.key
        key = row - 1, col, tab
        color = self.cell_attributes[key]["bordercolor_bottom"]
        return tuple(c / 255.0 for c in color_pack2rgb(color))

    def _get_bottom_line_color(self):
        """Returns color rgb tuple of bottom line"""

        color = self.cell_attributes[self.key]["bordercolor_bottom"]
        return tuple(c / 255.0 for c in color_pack2rgb(color))

    def _get_left_line_color(self):
        """Returns color rgb tuple of left line"""

        row, col, tab = self.key
        key = row, col - 1, tab
        color = self.cell_attributes[key]["bordercolor_right"]
        return tuple(c / 255.0 for c in color_pack2rgb(color))

    def _get_right_line_color(self):
        """Returns color rgb tuple of right line"""

        color = self.cell_attributes[self.key]["bordercolor_right"]
        return tuple(c / 255.0 for c in color_pack2rgb(color))

    def _get_topleft_right_line_color(self):
        """Returns color rgb tuple of right line of top left cell"""

        row, col, tab = self.key
        key = row - 1, col - 1, tab
        color = self.cell_attributes[key]["bordercolor_right"]
        return tuple(c / 255.0 for c in color_pack2rgb(color))

    def _get_topleft_bottom_line_color(self):
        """Returns color rgb tuple of bottom line of top left cell"""

        row, col, tab = self.key
        key = row - 1, col - 1, tab
        color = self.cell_attributes[key]["bordercolor_bottom"]
        return tuple(c / 255.0 for c in color_pack2rgb(color))

    # Widths
    # ------

    def _get_top_line_width(self):
        """Returns width of top line"""

        row, col, tab = self.key
        key = row - 1, col, tab
        return float(self.cell_attributes[key]["borderwidth_bottom"]) / 2.0

    def _get_bottom_line_width(self):
        """Returns width of bottom line"""

        return float(self.cell_attributes[self.key]["borderwidth_bottom"]) / 2.

    def _get_left_line_width(self):
        """Returns width of left line"""

        row, col, tab = self.key
        key = row, col - 1, tab
        return float(self.cell_attributes[key]["borderwidth_right"]) / 2.0

    def _get_right_line_width(self):
        """Returns width of right line"""

        return float(self.cell_attributes[self.key]["borderwidth_right"]) / 2.0

    def _get_topleft_right_line_width(self):
        """Returns width of right line of top left cell"""

        row, col, tab = self.key
        key = row - 1, col - 1, tab
        return float(self.cell_attributes[key]["borderwidth_right"]) / 2.0

    def _get_topleft_bottom_line_width(self):
        """Returns width of bottom line of top left cell"""

        row, col, tab = self.key
        key = row - 1, col - 1, tab
        return float(self.cell_attributes[key]["borderwidth_bottom"]) / 2.0

    # Drawing
    # -------

    def _draw_line(self, start_point, end_point):
        """Draws a line without setting color or width

        Parameters
        ----------
        start_point: 2 tuple of Integer
        \tStart point of line
        end_point
        \tEnd point of line

        """

        self.context.move_to(*start_point)
        self.context.line_to(*end_point)
        self.context.stroke()

    def _draw_left_line(self):
        """Draws left line setting color and width"""

        self.context.set_source_rgb(*self._get_left_line_color())
        self.context.set_line_width(self._get_left_line_width())
        self._draw_line(*self._get_left_line_coordinates())

    def _draw_right_line(self):
        """Draws right line setting color and width"""

        self.context.set_source_rgb(*self._get_right_line_color())
        self.context.set_line_width(self._get_right_line_width())
        self._draw_line(*self._get_right_line_coordinates())

    def _draw_top_line(self):
        """Draws top line setting color and width"""

        self.context.set_source_rgb(*self._get_top_line_color())
        self.context.set_line_width(self._get_top_line_width())
        self._draw_line(*self._get_top_line_coordinates())

    def _draw_bottom_line(self):
        """Draws bottom line setting color and width"""

        self.context.set_source_rgb(*self._get_bottom_line_color())
        self.context.set_line_width(self._get_bottom_line_width())
        self._draw_line(*self._get_bottom_line_coordinates())

    def _draw_tlr_line(self):
        """Draws bottom line setting color and width"""

        self.context.set_source_rgb(*self._get_topleft_right_line_color())
        self.context.set_line_width(self._get_topleft_right_line_width())
        self._draw_line(*self._get_topleft_right_line_coordinates())

    def _draw_tlb_line(self):
        """Draws bottom line setting color and width"""

        self.context.set_source_rgb(*self._get_topleft_bottom_line_color())
        self.context.set_line_width(self._get_topleft_bottom_line_width())
        self._draw_line(*self._get_topleft_bottom_line_coordinates())

    def draw(self):
        """Draws cell border to context"""

        # Lines should have a square cap to avoid ugly edges
        self.context.set_line_cap(cairo.LINE_CAP_SQUARE)

        # Sort lines from thinnest to thickest
        width_func = [
            (self._get_left_line_width(),
             -sum(self._get_left_line_color()), self._draw_left_line),
            (self._get_right_line_width(),
             -sum(self._get_right_line_color()), self._draw_right_line),
            (self._get_top_line_width(),
             -sum(self._get_top_line_color()), self._draw_top_line),
            (self._get_bottom_line_width(),
             -sum(self._get_bottom_line_color()), self._draw_bottom_line),
            (self._get_topleft_right_line_width(),
             -sum(self._get_topleft_right_line_color()), self._draw_tlr_line),
            (self._get_topleft_bottom_line_width(),
             -sum(self._get_topleft_bottom_line_color()), self._draw_tlb_line),
        ]

        width_func.sort()

        for _, _, draw_func in width_func:
            draw_func()
