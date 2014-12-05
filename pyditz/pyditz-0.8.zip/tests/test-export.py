"""
Database export tests.
"""

from ditz.database import DitzDB, DitzError
from nose.tools import raises


def test_html(name="example"):
    "Test exporting HTML"

    db = DitzDB.read(name)
    db.export('html', name + "-html")


def test_zip(name="example"):
    "Test exporting HTML ZIP file."

    db = DitzDB.read(name)
    db.export('html', name + "-issues.zip")


@raises(DitzError)
def test_zip_fail(name="example"):
    "Test exporting HTML ZIP file (not clobbering existing directory)."

    db = DitzDB.read(name)
    db.export('html', name + "-html.zip")
