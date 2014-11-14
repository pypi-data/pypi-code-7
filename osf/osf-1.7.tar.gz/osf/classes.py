from .timeutils import milliseconds_to_hhmmss
from modgrammar import ParseError


class ParentlessNoteError(ParseError):
    def __init__(self, line=-1):
        self.line = line

    def __str__(self):
        return "Parentless note at line " + str(self.line)


class Header:
    def __init__(self):
        self.kv = {}
        self.v = []


class OSFLine():
    def __init__(self):
        self.time = None
        self.text = ""
        self.link = None
        self.tags = []
        self.notes = []
        self._line = -1

    def osf(self, depth=0):
        parts = []
        if depth:
            parts.append('-' * depth)
        if self.time is not None:
            parts.append(milliseconds_to_hhmmss(self.time))
        parts.append(self.text)
        if self.link:
            parts.append("<" + self.link + ">")
        parts.extend(["#" + tag for tag in self.tags])
        return " ".join(parts)
