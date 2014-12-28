from __future__ import print_function
from gost89 import gosthash

if str is bytes:
    def bytes(x, enc):
        return x

def test_gosthash():
    data = '12345678901234567890123456789011';
    expect_ret = 'v\x86\xf3\xf4\xb1\x13\xaa\xdc\x97\xbc\xa9\xea\x05OA\x82\x1f\x06v\xc5\xc2\x8f\xfb\x98~AyzV\x8e\x1e\xd4'

    ret = gosthash(data)
    assert ret == bytes(expect_ret, 'latin')


def test_gosthash2():
    data = '123123'
    expect_ret = '4\xd4\xda,\x04\xe9\xc1\xce\xb93( i\xc8da}\x94\xed|\xc5\xc0\xa9\x84\x0c\x0c\x1a\x99b\x9d\xf67'
    ret = gosthash(data)
    assert ret == bytes(expect_ret, 'latin')


def test_gosthash3():
    data = 'IGNORE THIS FILE. This file does nothing, contains no useful data, and might go away in future releases.  Do not depend on this file or its contents.';
    ret = gosthash(data)
    expect_ret = '\xe91-\x13\xd0\xe0\xd3\x9a\xa4\xa0\x0cw\xdc\xfbf\x18\x83\xdd\x0e\xd8!\x8a\xf4\x8a\x14ah\xfc`\xf0\x14\xdc'
    assert ret == bytes(expect_ret, 'latin')
    for x in range(10000):
        ret = gosthash(data)
        assert ret == bytes(expect_ret, 'latin')
        ret = gosthash(data+'\0')
        assert ret != bytes(expect_ret, 'latin')

