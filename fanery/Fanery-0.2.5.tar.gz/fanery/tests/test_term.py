from fanery._term import parse_term, Hict, UUID, is_uuid, is_dict, is_number
from fanery._random import rand_uuid, rand_num

# -- test helper functions --------------------------


def gen_dict():
    gen_ints = lambda: [str(rand_num(i, dec=False)) for i in xrange(1, 11)]
    gen_floats = lambda: [str(rand_num(i)) for i in xrange(1, 11)]
    gen_uuids = lambda: (str(rand_uuid()), rand_uuid().hex, rand_uuid())

    return dict(ints=gen_ints(),
                floats=gen_floats(),
                uuids=gen_uuids())

# -- real tests -------------------------------------


def test_parse_term_Hict():
    dct = gen_dict()
    dct.update(dicts=[gen_dict() for _ in range(10)])
    for d in dct['dicts']:
        d.update(dicts=[gen_dict() for _ in range(10)])

    assert is_dict(dct)

    term = parse_term(dct, dict_type=Hict)

    assert isinstance(term, Hict)
    assert is_dict(term)

    for u in term.uuids:
        assert isinstance(u, UUID)
        assert is_uuid(u)

    for i in term.ints:
        assert isinstance(i, (int, long))
        assert is_number(i)

    for f in term.floats:
        assert isinstance(f, (int, long, float))
        assert is_number(f)

    # recursive parse_term

    for dct in term.dicts:
        assert isinstance(dct, Hict)
        assert is_dict(dct)

        for u in dct.uuids:
            assert isinstance(u, UUID)
            assert is_uuid(u)

        for i in dct.ints:
            assert isinstance(i, (int, long))
            assert is_number(i)

        for f in dct.floats:
            assert isinstance(f, (int, long, float))
            assert is_number(f)

        for d in dct.dicts:
            assert isinstance(d, Hict)
            assert is_dict(d)

            for u in d.uuids:
                assert isinstance(u, UUID)
                assert is_uuid(u)

            for i in d.ints:
                assert isinstance(i, (int, long))
                assert is_number(i)

            for f in d.floats:
                assert isinstance(f, (int, long, float))
                assert is_number(f)

# -- tests run -------------------------------------------


def main():
    from random import shuffle
    tests = [(k, v) for k, v in globals().iteritems()
             if k.startswith('test_') and callable(v)]
    shuffle(tests)

    from fanery import timecall, memory_profile, line_profile  # noqa
    for name, test in tests:
        #memory_profile(test)()
        #line_profile(test)()
        timecall(test)()

if __name__ == '__main__':
    main()
