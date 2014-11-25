import olefile

f = open('tests/test.doc', 'rb')
oledata = f.read()
f.seek(0)

print 'isOleFile with file object:'
print olefile.isOleFile(f)

print 'OleFile.open with file object:'
ole = olefile.OleFileIO(f)
print ole.listdir()
ole.close()
print ''


print 'isOleFile with data in bytes:'
print olefile.isOleFile(oledata)

print 'OleFile.open with data in bytes:'
ole = olefile.OleFileIO(oledata)
print ole.listdir()
ole.close()
print ''

print 'isOleFile with non-OLE data in bytes:'
print olefile.isOleFile(b'TEST' + b' '*olefile.MINIMAL_OLEFILE_SIZE)

