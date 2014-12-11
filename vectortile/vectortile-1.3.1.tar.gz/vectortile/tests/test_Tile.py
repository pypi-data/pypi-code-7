import unittest2
from .. import Tile


class TileTest(unittest2.TestCase):
    def test_tile(self):
        d = {'A': 1}
        h = {'source': 'test_Tile'}
        tile = Tile.fromdata(d, meta=h)
        header, data = tile.unpack()
        self.assertEqual(header['length'], 1)
        self.assertEqual(header['source'], h['source'])
        self.assertEqual(data[0]['A'], d['A'])
        self.assertEqual(repr(tile), repr(eval(repr(tile))))

    def test_empty(self):
        d = []
        h = {'source': 'test_Tile'}
        tile = Tile.fromdata(d, meta=h)
        header, data = tile.unpack()
        self.assertEqual(header['length'], 0)
        self.assertEqual(len(data), 0)

