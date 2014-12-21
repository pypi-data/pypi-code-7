from gost89 import gosthash


def test_gosthash():
    data = '12345678901234567890123456789011';
    expect_ret = '7686f3f4b113aadc97bca9ea054f41821f0676c5c28ffb987e41797a568e1ed4'

    ret = gosthash(data)
    print 'got ret', ret
    assert len(ret) == 32, repr(ret)
    assert ret.encode('hex') == expect_ret


def test_gosthash2():
    data = '123123'
    ret = gosthash(data)
    expect_ret = '34d4da2c04e9c1ceb933282069c864617d94ed7cc5c0a9840c0c1a99629df637'
    assert ret.encode('hex') == expect_ret


def test_gosthash3():
    data = 'IGNORE THIS FILE. This file does nothing, contains no useful data, and might go away in future releases.  Do not depend on this file or its contents.';
    ret = gosthash(data)
    expect_ret = 'e9312d13d0e0d39aa4a00c77dcfb661883dd0ed8218af48a146168fc60f014dc'
    assert ret.encode('hex') == expect_ret
    for x in range(10000):
        ret = gosthash(data)
        assert ret.encode('hex') == expect_ret
        ret = gosthash(data+'\0')
        assert ret.encode('hex') != expect_ret

