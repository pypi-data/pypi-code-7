import unittest2
from vectortile import TileBounds, Bbox


class TileTest(unittest2.TestCase):
    def test_tile_bounds(self):
        # default tile bounds is the world tile
        self.assertEqual(TileBounds().get_bbox(), Bbox())

        # make sure Bounds to Bbox and back is reflexive
        bounds = TileBounds('12321')
        bbox = bounds.get_bbox()
        self.assertEqual(bbox, Bbox(56.25, -11.25, 67.5, -5.625))
        self.assertEqual(TileBounds.from_bbox_best_fit(bbox), bounds)

        # test __str__ and __repr__
        self.assertEqual("TileBounds('12321')", repr(eval(repr(bounds))))

        # parents and children
        self.assertEqual(bounds.get_parent(), '1232')
        self.assertListEqual(bounds.get_children(), ['123210', '123211', '123212', '123213'])
        self.assertListEqual(bounds.get_ancestors(), ['1232', '123', '12', '1', ''])

        # from point
        self.assertEqual(TileBounds.from_point(lon=10, lat=10, zoom_level=0), TileBounds())
        self.assertEqual(TileBounds.from_point(lon=10, lat=10, zoom_level=1).get_bbox(), Bbox(0, 0, 180, 90))

        # from bbox
        self.assertEqual(TileBounds.from_bbox_best_fit(Bbox(0, 0, 180, 90)).get_bbox(), Bbox(0, 0, 180, 90))
        self.assertEqual(TileBounds.from_bbox_best_fit(Bbox(56.25, -11.25, 67.5, -5.625)).get_bbox(),
                         Bbox(56.25, -11.25, 67.5, -5.625))
        self.assertEqual(TileBounds.from_bbox_best_fit(Bbox(56, -11.25, 68, -5.625)).get_bbox(),
                         Bbox(+045.00000, -011.25000, +067.50000, +000.00000))

        # center
        self.assertDictEqual(TileBounds().get_center(), dict(lat=0.0, lon=0.0))
        self.assertDictEqual(TileBounds('0').get_center(), dict(lat=-45.0, lon=-90.0))

        # boundary cases
        self.assertListEqual(TileBounds().get_ancestors(), [])
        self.assertEqual(TileBounds.from_point(lon=180, lat=0, zoom_level=1).get_bbox(),
                         Bbox(-180, 0, 0, 90))
        self.assertEqual(TileBounds.from_point(lon=0, lat=90, zoom_level=1).get_bbox(),
                         Bbox(0, 0, 180, 90))

