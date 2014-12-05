# -*- coding: utf8 -*-
from xlsxwriter.format import Format
from xlsxwriter.utility import xl_cell_to_rowcol, xl_rowcol_to_cell_fast


class XlsxCursor(object):
    """
    :type workbook: xlsxwriter.Workbook
    :type worksheet: xlsxwriter.worksheet.Worksheet
    """

    def __init__(self, workbook, worksheet, cell_str=None, row=0, column=0, columns_colors=None):
        self._formats = {}
        self.workbook = workbook
        self.worksheet = worksheet
        self.default_format = {}
        if cell_str:
            self.row, self.column = xl_cell_to_rowcol(cell_str)
        else:
            self.row = row
            self.column = column
        self.start_column = self.column
        self.start_row = self.row
        self.column_colors = columns_colors or {}

    def reset(self):
        self.row = self.start_row
        self.column = self.start_column

    def _get_format(self, format_dict):
        if isinstance(format_dict, Format):
            return format_dict

        current_format = dict(self.default_format.items() + format_dict.items())
        color = self.column_colors.get(self.column)
        if color:
            current_format['bg_color'] = color

        format_key = tuple(current_format.iteritems())
        if format_key in self._formats:
            format_object = self._formats[format_key]
        else:
            format_object = self.workbook.add_format(current_format)
            self._formats[format_key] = format_object

        return format_object

    def write_url(self, url, title, cell_format, width=1):
        self.worksheet.write_url(self.row, self.column, url, cell_format, title)
        self.column += width

    def write_string(self, string, cell_format):
        self.worksheet.write_string(self.row, self.column, string, cell_format)
        self.column += 1

    def write(self, value, width=1, height=1, format_params=None):
        cell_format = self._get_format(format_params or {})

        if width == 1 and height == 1:
            self.worksheet.write(
                self.row,
                self.column,
                value,
                cell_format
            )
        else:
            self.worksheet.merge_range(
                self.row,
                self.column,
                self.row + height - 1,
                self.column + width - 1,
                value,
                cell_format
            )
        self.column += width

    def merge_cells(self, width=1, height=1, format_params=None):
        cell_format = self._get_format(format_params or {})

        self.worksheet.merge_range(
            self.row,
            self.column,
            self.row + height - 1,
            self.column + width - 1,
            "",
            cell_format
        )

    def insert_chart(self, chart, chart_format=None):
        chart_format = chart_format or {}
        self.worksheet.insert_chart(self.row, self.column, chart, chart_format)

    def add_comment(self, comment_text, comment_format=None):
        default_format = {'x_scale': 1.5, 'y_scale': 0.3}
        self.worksheet.write_comment(self.row, self.column, comment_text, comment_format or default_format)

    def get_cell(self, row=None, column=None):
        row = row or self.row
        column = column or self.column
        return xl_rowcol_to_cell_fast(row, column)

    def write_rich_string(self, string_args, format_params=None):
        cell_format = self._get_format(format_params or {})
        string_args.append(cell_format)
        self.worksheet.write_rich_string(self.row, self.column, *string_args)

    def __call__(self, value, width=1, height=1, format_params=None):
        self.write(value, width, height, format_params)

    def change_cursor(self, row=None, column=None):
        if row is not None:
            self.row = row
        if column is not None:
            self.column = column

    def set_start_position(self, row=0, column=0):
        self.start_row = row
        self.start_column = column

    def write_sum_formula(self, cells, format_params=None):
        formula = '{{=SUM({0})}}'.format(','.join(cells))
        self.write_formula(formula, 1, format_params)

    def write_sum_range_formula(self, cells, format_params=None):
        formula = '{{=SUM({0}:{1})}}'.format(cells[0], cells[-1])
        self.write_formula(formula, 1, format_params)

    def write_formula(self, formula, width=1, format_params=None):
        cell_format = self._get_format(format_params or {})
        self.worksheet.write_formula(self.row, self.column, formula, cell_format)
        self.column += width

    def cr(self, number=1):
        """
        Переход на следующую строку
        """
        self.row += number
        self.column = self.start_column

    def set_row_height(self, height, format_params=None):
        cell_format = self._get_format(format_params or {})
        self.worksheet.set_row(self.row, height, cell_format)

    def set_column_width(self, width):
        self.worksheet.set_column(self.column, self.column, width)

    def space(self, width=1):
        self.column += width

    def insert_image(self, img_path, options=None):
        u"""
        Вставляет картинку в положении курсора
        img_path - абсолютный путь к изображению
        """
        options = options or {}
        self.worksheet.insert_image(self.row, self.column, img_path, options)
