import bcrypt


WORK_FACTOR = 12  # 12=bcrypt default


def check(plain, hashed):
    plain = _encode(plain)
    hashed = _encode(hashed)
    return _constant_time_equal(bcrypt.hashpw(plain, hashed), hashed)


def hash(plain):
    plain = _encode(plain)
    return unicode(bcrypt.hashpw(plain, bcrypt.gensalt(WORK_FACTOR)))


def _constant_time_equal(a, b):
    # adapted from <http://throwingfire.com/storing-passwords-securely/>,
    # see also <http://codahale.com/a-lesson-in-timing-attacks/>
    if len(a) != len(b):
        return False

    result = 0
    for x, y in zip(a, b):
        result |= ord(x) ^ ord(y)
    return result == 0


def _encode(text):
    if isinstance(text, unicode):
        text = text.encode('utf8')
    return text
