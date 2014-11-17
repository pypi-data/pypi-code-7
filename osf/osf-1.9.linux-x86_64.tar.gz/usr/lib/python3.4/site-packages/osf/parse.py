from .grammar import Line
from .classes import Header
from modgrammar import ParseError

LineParser = Line.parser()


def parse_line(line):
    line = line.strip()

    if not line:
        return None

    return LineParser.parse_string(line)


def parse_header_line(line, header):
    if len(line) == 0:
        return

    colon_pos = line.find(':')

    if colon_pos == -1:
        header.v.append(line)
    else:
        k = line[:colon_pos].lower()
        v = line[colon_pos + 1:].strip()
        header.kv[k] = v


def parse_header(lines):
    header_start = -1
    header_end = -1

    header = None

    num = -1

    for line in lines:
        line = line.strip()

        num += 1

        if line == 'HEADER':
            header_start = num
            header = Header()
            continue
        elif line == '/HEADER' and header_start != -1:
            header_end = num
            break

        if header_start != -1: # in header
            parse_header_line(line, header)

    if header_start == -1 or header_end == -1:
        header_start = -1
        header = None

    return header_start, header_end, header


def parse_lines(lines):
    num = 0

    llines = []
    h_start, h_end, header = parse_header(lines)

    if h_start != -1:
        lines = lines[h_end + 1:]

    for line in lines:
        num += 1

        lline = None

        try:
            lline = parse_line(line)
        except ParseError as e:
            e.line = num
            llines.append(e)

        if lline:
            llines.append(lline)
            lline._line = num

    return header, llines
