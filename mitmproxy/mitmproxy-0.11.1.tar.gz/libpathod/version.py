IVERSION = (0, 11, 1)
VERSION = ".".join(str(i) for i in IVERSION)
MINORVERSION = ".".join(str(i) for i in IVERSION[:2])
NAME = "pathod"
NAMEVERSION = NAME + " " + VERSION

NEXT_MINORVERSION = list(IVERSION)
NEXT_MINORVERSION[1] += 1
NEXT_MINORVERSION = ".".join(str(i) for i in NEXT_MINORVERSION[:2])
