try:
    unicode
except NameError:
    unicode = str 
else:
    unicode = unicode
try:
    bytes 
except NameError:
    bytes = str
else:
    bytes = bytes
