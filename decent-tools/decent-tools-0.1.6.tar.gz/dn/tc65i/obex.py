import functools
import array
import struct
import logging
import os
import time
import collections
import xml.etree.ElementTree as ET

HEADER_COUNT                   = 0xC0
HEADER_NAME                    = 0x01
HEADER_TYPE                    = 0x42
HEADER_LENGTH                  = 0xC3
HEADER_TIME                    = 0x44
HEADER_DESCRIPTION             = 0x05
HEADER_TARGET                  = 0x46
HEADER_HTTP                    = 0x47
HEADER_BODY                    = 0x48
HEADER_END_OF_BODY             = 0x49
HEADER_WHO                     = 0x4A
HEADER_CONNECTION_ID           = 0xCB
HEADER_APP_PARAMETERS          = 0x4C
HEADER_AUTH_CHALLENGE          = 0x4D
HEADER_AUTH_RESPONSE           = 0x4E
HEADER_CREATOR_ID              = 0xCF
HEADER_WAN_UUID                = 0x50
HEADER_OBJECT_CLASS            = 0x51
HEADER_SESSION_PARAMETERS      = 0x52
HEADER_SESSION_SEQUENCE_NUMBER = 0x93

REQUEST_CONNECT    = 0x80
REQUEST_DISCONNECT = 0x81
REQUEST_PUT        = 0x02
REQUEST_GET        = 0x03
REQUEST_SETPATH    = 0x85
REQUEST_SETPATH2   = 0x86
REQUEST_SESSION    = 0x87
REQUEST_ABORT      = 0xFF
REQUEST_FINAL      = 0x80

FLAG_SETPATH_CREATE        = 0x00
FLAG_SETPATH_NOCREATE      = 0x02
FLAG_SETPATH_PARENT_FOLDER = 0x03

RESPONSE_SUCCESS    = 0x20
RESPONSE_CONTINUE   = 0x10
RESPONSE_CREATED    = 0x21
RESPONSE_BADREQUEST = 0x40
RESPONSE_FINAL      = 0x80

logger = logging.getLogger(__name__)

bytestoint = lambda bytes, sh=0: ((bytes[-1] << sh) + bytestoint(bytes[:-1], sh+8)) if len(bytes) > 0 else 0
shorttobytes = lambda shrt: strtobytes(struct.pack('!H', shrt)) # unsigned short 2 bytes
longtobytes = lambda lng: strtobytes(struct.pack('!L', lng)) # unsigned int 4 bytes

bytestostr = lambda bytes: array.array('B', bytes).tostring()
strtobytes = lambda st: array.array('B', st).tolist()

buildrequest = lambda opcode, data: [opcode] + shorttobytes(3 + len(data)) + data
buildheader = lambda type, data: [type] + shorttobytes(3 + len(data)) + data
isvalid_responsecode = lambda code: (code & RESPONSE_SUCCESS or code & RESPONSE_CREATED or code & RESPONSE_CONTINUE)

parsenullstrfunc = lambda data: (3 + bytestoint(data[1:3]), bytestostr(data[3:3+bytestoint(data[1:3])]))
parselenfunc = lambda data: (1 + 4, bytestoint(data[1:1+4]))
getheaderfunc = lambda type: parselenfunc if (type == HEADER_COUNT or type == HEADER_LENGTH) else parsenullstrfunc
getheaderlen = lambda data: getheaderfunc(data[0])(data)[0]
getheader = lambda data: getheaderfunc(data[0])(data)[1]

parseheaders = lambda data: (
    dict() if len(data) == 0 else (
        dict(
            [(data[0],getheader(data))] + 
            parseheaders(data[getheaderlen(data):]).items()
            )
        )
    )

class ObexException(Exception):
    pass

class Triplet:
    def __init__(self, tag, len, value):
        self.tag = tag
        self.len = len
        self.value = value

    @classmethod
    def frombytes(cls, bytes):
        return cls(bytes[0], bytes[1], bytes[2:])

    def bytes(self):
        return [self.tag, self.len] + self.value

def proctriplet(serdev, triplet):
    header = buildheader(HEADER_APP_PARAMETERS, triplet.bytes())
    _, hdrs = procrequest(serdev, REQUEST_PUT | REQUEST_FINAL, header)
    res = Triplet.frombytes(hdrs[HEADER_APP_PARAMETERS])
    return bytestoint(strtobytes(res.value))

def _writerequest(serdev, request):
    serdev.flushInput()
    serdev.write(bytestostr(request))
    serdev.flush()

def _readresponse(serdev, timeout):
    s = time.time()
    code = ''
    while time.time() - s < timeout or timeout == None:
        code = serdev.read(1)
        if len(code) > 0:
            break
        time.sleep(0.001)
    if len(code) == 0:
        raise ObexException('Empty reply, make sure obex mode is configured on the tc65i')
    logger.debug('response header {:#x}'.format(ord(code)))
    len_str = serdev.read(2)
    length = bytestoint(strtobytes(len_str)) - 3 # code and length are 3 bytes
    logger.debug('response length {:#x}'.format(length))
    data = serdev.read(length)
    logger.debug('response: {}'.format(map(lambda x:hex(ord(x)), data)))
    return ord(code), length, strtobytes(data)

def connect(serdev):
    fsuid = [0x6b, 0x01, 0xcb, 0x31, 0x41, 0x06, 0x11, 0xd4, 0x9a, 0x77, 0x00, 0x50, 0xda, 0x3f, 0x47, 0x1f]
    header = buildheader(HEADER_TARGET, fsuid)
    info = [0x13, 0x00] + shorttobytes(0xffff) #version, flags, max packet length
    procrequest(serdev, REQUEST_CONNECT, info + header)

def disconnect(serdev):
    procrequest(serdev, REQUEST_DISCONNECT, shorttobytes(3))

def procrequest(serdev, opcode, data, timeout=10):
    request = buildrequest(opcode, data)
    logger.debug('sending {} bytes: {}'.format(len(request), map(lambda x:hex(x), request)))

    _writerequest(serdev, request)
    code, length, data = _readresponse(serdev, timeout=timeout)
    logger.debug("{:#x} len={}: {}".format(code, length, data))

    if not isvalid_responsecode(code):
        raise ObexException('Unknown response code {:#x}'.format(code))
    if code & RESPONSE_BADREQUEST:
        raise ValueError('Bad request received opcode: {:#x} data: {!s}'.format(opcode, data))

    headers = parseheaders(data)

    return code, headers

def procbodyrequest(serdev, opcode, data, timeout=10):
    def reqiterator():
        code, headers = procrequest(serdev, opcode, data, timeout=timeout)
        yield headers
        while code & RESPONSE_CONTINUE:
            code, headers = procrequest(serdev, REQUEST_GET | REQUEST_FINAL, shorttobytes(3), timeout=timeout)
            yield headers

    body = ''
    for headers in reqiterator():
        try:
            body += headers[HEADER_BODY]
        except KeyError, e:
            logger.info("Body header not found for request {:#x}, possibly the last request".format(opcode))

    return body

def getfile(serdev, path):
    parson = path.split('/', 1)
    if len(parson) > 1: # # go further inside
        changedir(serdev, parson[0])
        res = getfile(serdev, parson[1])
        changedir(serdev, '..')
    elif len(parson) == 1: # time to get it
        destname = parson[0]
        namehdr = buildheader(HEADER_NAME, strtobytes(destname.encode('utf-16be')))
        logger.debug('namehdr: {}'.format(map(hex, namehdr)))
        res = procbodyrequest(serdev, REQUEST_GET | REQUEST_FINAL, namehdr)
    return res

def putfile(serdev, path, file):
    MAX_PART_LEN = 512
    parson = path.split('/', 1)
    if len(parson) > 1: # # go further inside
        changedir(serdev, parson[0])
        putfile(serdev, parson[1], file)
        changedir(serdev, '..')
    elif len(parson) == 1: # time to put it
        destname = parson[0]
        stat = os.fstat(file.fileno())
        logger.info('Putting file({} bytes) {} with chunk size of {}'.format(stat.st_size, destname, MAX_PART_LEN))
        first = True
        for chunk in iter(lambda: file.read(MAX_PART_LEN), ''):
            logger.debug('Putting file chunk')
            last = len(chunk) < MAX_PART_LEN
            headers = []
            logger.debug('chunk first:{} last:{}'.format(first, last))
            if first:
                first = False
                namehdr = buildheader(HEADER_NAME, strtobytes(destname.encode('utf-16be')))
                logger.debug('namehdr: {}'.format(map(hex, namehdr)))
                headers.extend(namehdr)
                lenhdr = [HEADER_LENGTH] + longtobytes(stat.st_size)
                logger.debug('lenhdr: {}'.format(map(hex, lenhdr)))
                headers.extend(lenhdr)
                timehdr = buildheader(HEADER_TIME, strtobytes(time.strftime('%Y%m%dT%H%M%S', time.localtime(stat.st_mtime))))
                logger.debug('timehdr: {}'.format(map(hex, timehdr)))
                headers.extend(timehdr)

            bodyhdr = buildheader(HEADER_END_OF_BODY if last else HEADER_BODY, strtobytes(chunk))
            logger.debug('bodyhdr: {}'.format(map(hex, bodyhdr)))
            headers.extend(bodyhdr)
            req = (REQUEST_PUT | REQUEST_FINAL) if last else REQUEST_PUT
            procrequest(serdev, req, headers)

def listdir(serdev):
    header = buildheader(HEADER_TYPE, strtobytes('x-obex/folder-listing'))
    xmlstr = procbodyrequest(serdev, REQUEST_GET | REQUEST_FINAL, header)
    files = ET.fromstring(xmlstr)
    return files
    
def removeobject(serdev, path):
    parson = path.split('/', 1)

    if len(parson) > 1: # go further inside
        changedir(serdev, parson[0])
        removeobject(serdev, parson[1]) # remove whatever it is
        changedir(serdev, '..')
    elif len(parson) == 1: # time to remove it
        object = parson[0]
        isfolder = len(filter(lambda k: k.attrib['name'] == object, listdir(serdev).findall('folder'))) > 0
        if isfolder: # then remove kids first
            changedir(serdev, object)
            for k in listdir(serdev):
                removeobject(serdev, k.attrib['name']) # remove whatever it is
            changedir(serdev, '..')
        logger.info('Removing object ' + object)
        namehdr = buildheader(HEADER_NAME, strtobytes(parson[0].encode('utf-16be')))
        logger.debug('namehdr: {}'.format(map(hex, namehdr)))
        procrequest(serdev, REQUEST_PUT | REQUEST_FINAL, namehdr)

def makedir(serdev, path):
    parson = path.split('/', 1)
    if len(parson) > 0: # go further inside
        changedir(serdev, parson[0], create=True)
        if len(parson) > 1: makedir(serdev, parson[1])
        changedir(serdev, '..')

def changedir(serdev, dir, create=False):
    if dir == None or dir == '':
        logger.info('Ignoring invalid directory name \'{}\''.format(dir))
        return
    elif dir == '/' or  dir.lower() == 'a:' or dir.lower() == 'a:/':
        dir = ''

    if dir == '..':
        flag = FLAG_SETPATH_PARENT_FOLDER
        header = []
    else:
        flag = FLAG_SETPATH_CREATE if create else FLAG_SETPATH_NOCREATE
        header = buildheader(HEADER_NAME, strtobytes(dir.encode('utf-16be')))    

    logger.info('Changing to {}'.format(dir))
    procrequest(serdev, REQUEST_SETPATH, [flag, 0x00] + header)

def erasestorage(serdev):
    erasehdr = buildheader(HEADER_APP_PARAMETERS, [0x31, 0x00])
    logger.debug('erasehdr: {}'.format(map(hex, erasehdr)))
    procrequest(serdev, REQUEST_PUT | REQUEST_FINAL, erasehdr, timeout=100)

def abort(serdev):
    procrequest(serdev, REQUEST_ABORT | REQUEST_FINAL, [])

def main():
    pass

if __name__ == '__main__':
    main()
