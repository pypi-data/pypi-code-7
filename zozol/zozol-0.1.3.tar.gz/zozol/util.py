import base64
import StringIO


def to_pem(data, name):
    ret = StringIO.StringIO()
    ret.write('-----BEGIN {}-----\n'.format(name.upper()))
    for x in range(0, len(data), 48):
        ret.write(base64.b64encode(data[x:x+48]))
        ret.write('\n')
    ret.write('-----END {}-----\n'.format(name.upper()))
    return ret.getvalue()
