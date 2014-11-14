import pytest
import osf
import osf.grammar


def do_real_test(file):
    f = open(file)
    lines = f.readlines()
    f.close()

    header, lines = osf.parse_lines(lines)
    result = osf.objectify_lines(lines)
    #print("\n".join([str(line) for line in result]))


def test_nsfw_88():
    do_real_test('./test/data/nsfw-88.txt')


def test_anycast_51():
    do_real_test('./test/data/anycast-51.txt')
