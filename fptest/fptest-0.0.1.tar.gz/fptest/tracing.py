import re
import enum

__author__ = 'John Oxley'


class Trace:
    def __init__(self):
        self.outgoing_workorders = []


class WorkOrder:
    @staticmethod
    def balanced_braces(args):
        parts = []
        for arg in args:
            if '<' not in arg:
                continue
            chars = []
            n = 0
            for c in arg:
                if c == '<':
                    if n > 0:
                        chars.append(c)
                    n += 1
                elif c == '>':
                    n -= 1
                    if n > 0:
                        chars.append(c)
                    elif n == 0:
                        parts.append(''.join(chars).lstrip().rstrip())
                        chars = []
                elif n > 0:
                    chars.append(c)
        return parts

    def __init__(self, name=None, status=None):
        self.name = name
        self.status = status
        self.params = {}
        self.raw_params = {}

    def __str__(self):
        return "WO %s: %s" % (self.name, self.status)

    def add_param(self, name, values):
        if values is None:
            self.params[name] = []
        else:
            raw_values = WorkOrder.balanced_braces([values])
            self.raw_params[name] = raw_values
            decoded_values = [v.encode('latin1').decode('unicode_escape') for v in raw_values]
            self.params[name] = decoded_values


class ParserState(enum.Enum):
    looking_for_start = 1
    parsing_outgoing_wo = 2


def parse_trace_file(filename):
    """
    Parse a trace file, e.g. cartOrderTracing.00000.log
    :param filename:
    :return:
    """

    trace = Trace()

    outgoing_workorder = re.compile(r"^(?P<time>.{26}).+OUTGOING: For WO <(?P<wo>[^>]+)>.+<(?P<status>[^>]+)")
    param_re = re.compile(r"^Found param:<(?P<name>[^>]+)>, with value list : ?(?P<values>.+)?")

    parser_state = ParserState.looking_for_start

    wo = WorkOrder()
    i = 0
    with open(filename, 'r') as f:
        for line in f:
            i += 1
            if parser_state == ParserState.looking_for_start:
                wo_match = outgoing_workorder.match(line)
                if wo_match is not None:
                    wo.name = wo_match.group('wo')
                    wo.status = wo_match.group('status')
                    parser_state = ParserState.parsing_outgoing_wo
            elif parser_state == ParserState.parsing_outgoing_wo:
                match = param_re.match(line)
                if match is None:
                    trace.outgoing_workorders.append(wo)
                    wo = WorkOrder()
                    parser_state = ParserState.looking_for_start
                else:
                    wo.add_param(match.group('name'), match.group('values'))

        if parser_state == ParserState.parsing_outgoing_wo:
            trace.outgoing_workorders.append(wo)

    return trace