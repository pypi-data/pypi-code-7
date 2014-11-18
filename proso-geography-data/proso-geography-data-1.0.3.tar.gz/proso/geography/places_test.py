# -*- coding: utf-8 -*-
import unittest
import proso.geography.places as places
import os


class TestBasics(unittest.TestCase):

    def test_from_csv(self):
        data = places.from_csv(
            place_csv=os.environ['RESOURCES_DIR'] + '/place.csv',
            placerelation_csv=os.environ['RESOURCES_DIR'] + '/placerelation.csv',
            placerelation_related_places_csv=os.environ['RESOURCES_DIR'] + '/placerelation_related_places.csv',
            )
        self.assertEqual(len(data), 4)
        relations = sorted(list(data.head().relations)[0])
        self.assertEquals(relations, [(225, 'is_on_map'), (230, 'too_small_on_map')])
