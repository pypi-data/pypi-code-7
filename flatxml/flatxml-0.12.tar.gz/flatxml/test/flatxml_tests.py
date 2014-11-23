from nose.tools import *
from nose import with_setup
import flatxml
import os

def _get_path(path):
    return "%s/%s" % (os.path.dirname(os.path.realpath(__file__)), path)

def test_parse_file_no_write():
    xml_file = _get_path("files/simple.xml")
    result = flatxml.parse_file(xml_file)

    assert result['xml_a_[0]'] == 'Candy'
    assert result['xml_a_[1]'] == 'Candy2'
    assert result['xml_a_[2]'] == 'Candy3'
    assert result['xml_b_c'] == 'Sarah'
    assert result['xml_d_e_f'] == 'Carlos'
    assert result['xml_g'] == 'Wayne'    


def test_parse_blob():
    result = flatxml.parse_blob("""
        <movies>
            <horror>Frozen</horror>
            <documentary>Tokyo Drift</documentary>
        </movies>
    """)

    assert result['movies_horror'] == 'Frozen'
    assert result['movies_documentary'] == 'Tokyo Drift'


def test_attrs():
    result = flatxml.parse_blob("""
        <a attr="lkjlkjl">
            Value
        </a>
    """)

    assert result['a'] == 'Value'
