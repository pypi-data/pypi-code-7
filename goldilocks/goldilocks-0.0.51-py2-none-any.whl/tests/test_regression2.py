import unittest

import numpy as np

from goldilocks.goldilocks import Goldilocks
from goldilocks.strategies import NucleotideCounterStrategy

sequence_data = {
        "my_sample": {
            2: "NANANANANA",
            "X": "GATTACAGATTACAN",
            "one": "CATCANCAT",
            "three": "..A",
        },
        "my_other_sample": {
            2: "GANGANGAN",
            "X": "GATTACAGATTACAN",
            "one": "TATANTATA",
            "three": ".N.",
        }
}

EXPECTED_REGIONS = {
        2: {
            "my_sample": {
                0: {'A': 1, 'C': 0, 'T': 0, 'G': 0, 'N': 2},
                1: {'A': 2, 'C': 0, 'T': 0, 'G': 0, 'N': 1},
                2: {'A': 1, 'C': 0, 'T': 0, 'G': 0, 'N': 2},
                3: {'A': 2, 'C': 0, 'T': 0, 'G': 0, 'N': 1},
                4: {'A': 1, 'C': 0, 'T': 0, 'G': 0, 'N': 2},
                5: {'A': 2, 'C': 0, 'T': 0, 'G': 0, 'N': 1},
                6: {'A': 1, 'C': 0, 'T': 0, 'G': 0, 'N': 2},
                7: {'A': 2, 'C': 0, 'T': 0, 'G': 0, 'N': 1},
            },
            "my_other_sample": {
                0: {'A': 1, 'C': 0, 'T': 0, 'G': 1, 'N': 1},
                1: {'A': 1, 'C': 0, 'T': 0, 'G': 1, 'N': 1},
                2: {'A': 1, 'C': 0, 'T': 0, 'G': 1, 'N': 1},
                3: {'A': 1, 'C': 0, 'T': 0, 'G': 1, 'N': 1},
                4: {'A': 1, 'C': 0, 'T': 0, 'G': 1, 'N': 1},
                5: {'A': 1, 'C': 0, 'T': 0, 'G': 1, 'N': 1},
                6: {'A': 1, 'C': 0, 'T': 0, 'G': 1, 'N': 1},
                7: {'A': 1, 'C': 0, 'T': 0, 'G': 0, 'N': 1},
            },
            "total": {
                0: {'A': 2, 'C': 0, 'T': 0, 'G': 1, 'N': 3, "default": 6},
                1: {'A': 3, 'C': 0, 'T': 0, 'G': 1, 'N': 2, "default": 6},
                2: {'A': 2, 'C': 0, 'T': 0, 'G': 1, 'N': 3, "default": 6},
                3: {'A': 3, 'C': 0, 'T': 0, 'G': 1, 'N': 2, "default": 6},
                4: {'A': 2, 'C': 0, 'T': 0, 'G': 1, 'N': 3, "default": 6},
                5: {'A': 3, 'C': 0, 'T': 0, 'G': 1, 'N': 2, "default": 6},
                6: {'A': 2, 'C': 0, 'T': 0, 'G': 1, 'N': 3, "default": 6},
                7: {'A': 3, 'C': 0, 'T': 0, 'G': 0, 'N': 2, "default": 5},
            },
    },
        "X": {
            "my_sample": {
                0: {'A': 1, 'C': 0, 'T': 1, 'G': 1, 'N': 0},
                1: {'A': 1, 'C': 0, 'T': 2, 'G': 0, 'N': 0},
                2: {'A': 1, 'C': 0, 'T': 2, 'G': 0, 'N': 0},
                3: {'A': 1, 'C': 1, 'T': 1, 'G': 0, 'N': 0},
                4: {'A': 2, 'C': 1, 'T': 0, 'G': 0, 'N': 0},
                5: {'A': 1, 'C': 1, 'T': 0, 'G': 1, 'N': 0},
                6: {'A': 2, 'C': 0, 'T': 0, 'G': 1, 'N': 0},
                7: {'A': 1, 'C': 0, 'T': 1, 'G': 1, 'N': 0},
                8: {'A': 1, 'C': 0, 'T': 2, 'G': 0, 'N': 0},
                9: {'A': 1, 'C': 0, 'T': 2, 'G': 0, 'N': 0},
                10: {'A': 1, 'C': 1, 'T': 1, 'G': 0, 'N': 0},
                11: {'A': 2, 'C': 1, 'T': 0, 'G': 0, 'N': 0},
                12: {'A': 1, 'C': 1, 'T': 0, 'G': 0, 'N': 1},
            },
            "my_other_sample": {
                0: {'A': 1, 'C': 0, 'T': 1, 'G': 1, 'N': 0},
                1: {'A': 1, 'C': 0, 'T': 2, 'G': 0, 'N': 0},
                2: {'A': 1, 'C': 0, 'T': 2, 'G': 0, 'N': 0},
                3: {'A': 1, 'C': 1, 'T': 1, 'G': 0, 'N': 0},
                4: {'A': 2, 'C': 1, 'T': 0, 'G': 0, 'N': 0},
                5: {'A': 1, 'C': 1, 'T': 0, 'G': 1, 'N': 0},
                6: {'A': 2, 'C': 0, 'T': 0, 'G': 1, 'N': 0},
                7: {'A': 1, 'C': 0, 'T': 1, 'G': 1, 'N': 0},
                8: {'A': 1, 'C': 0, 'T': 2, 'G': 0, 'N': 0},
                9: {'A': 1, 'C': 0, 'T': 2, 'G': 0, 'N': 0},
                10: {'A': 1, 'C': 1, 'T': 1, 'G': 0, 'N': 0},
                11: {'A': 2, 'C': 1, 'T': 0, 'G': 0, 'N': 0},
                12: {'A': 1, 'C': 1, 'T': 0, 'G': 0, 'N': 1},
            },
            "total": {
                0: {'A': 2, 'C': 0, 'T': 2, 'G': 2, 'N': 0, "default": 6},
                1: {'A': 2, 'C': 0, 'T': 4, 'G': 0, 'N': 0, "default": 6},
                2: {'A': 2, 'C': 0, 'T': 4, 'G': 0, 'N': 0, "default": 6},
                3: {'A': 2, 'C': 2, 'T': 2, 'G': 0, 'N': 0, "default": 6},
                4: {'A': 4, 'C': 2, 'T': 0, 'G': 0, 'N': 0, "default": 6},
                5: {'A': 2, 'C': 2, 'T': 0, 'G': 2, 'N': 0, "default": 6},
                6: {'A': 4, 'C': 0, 'T': 0, 'G': 2, 'N': 0, "default": 6},
                7: {'A': 2, 'C': 0, 'T': 2, 'G': 2, 'N': 0, "default": 6},
                8: {'A': 2, 'C': 0, 'T': 4, 'G': 0, 'N': 0, "default": 6},
                9: {'A': 2, 'C': 0, 'T': 4, 'G': 0, 'N': 0, "default": 6},
                10: {'A': 2, 'C': 2, 'T': 2, 'G': 0, 'N': 0, "default": 6},
                11: {'A': 4, 'C': 2, 'T': 0, 'G': 0, 'N': 0, "default": 6},
                12: {'A': 2, 'C': 2, 'T': 0, 'G': 0, 'N': 2, "default": 6},
            },
    },
    "one": {
            "my_sample": {
                0: {'A': 1, 'C': 1, 'T': 1, 'G': 0, 'N': 0},
                1: {'A': 1, 'C': 1, 'T': 1, 'G': 0, 'N': 0},
                2: {'A': 1, 'C': 1, 'T': 1, 'G': 0, 'N': 0},
                3: {'A': 1, 'C': 1, 'T': 0, 'G': 0, 'N': 1},
                4: {'A': 1, 'C': 1, 'T': 0, 'G': 0, 'N': 1},
                5: {'A': 1, 'C': 1, 'T': 0, 'G': 0, 'N': 1},
                6: {'A': 1, 'C': 1, 'T': 1, 'G': 0, 'N': 0},
            },
            "my_other_sample": {
                0: {'A': 1, 'C': 0, 'T': 2, 'G': 0, 'N': 0},
                1: {'A': 2, 'C': 0, 'T': 1, 'G': 0, 'N': 0},
                2: {'A': 1, 'C': 0, 'T': 1, 'G': 0, 'N': 1},
                3: {'A': 1, 'C': 0, 'T': 1, 'G': 0, 'N': 1},
                4: {'A': 1, 'C': 0, 'T': 1, 'G': 0, 'N': 1},
                5: {'A': 1, 'C': 0, 'T': 2, 'G': 0, 'N': 0},
                6: {'A': 2, 'C': 0, 'T': 1, 'G': 0, 'N': 0},
            },
            "total": {
                0: {'A': 2, 'C': 1, 'T': 3, 'G': 0, 'N': 0, "default": 6},
                1: {'A': 3, 'C': 1, 'T': 2, 'G': 0, 'N': 0, "default": 6},
                2: {'A': 2, 'C': 1, 'T': 2, 'G': 0, 'N': 1, "default": 6},
                3: {'A': 2, 'C': 1, 'T': 1, 'G': 0, 'N': 2, "default": 6},
                4: {'A': 2, 'C': 1, 'T': 1, 'G': 0, 'N': 2, "default": 6},
                5: {'A': 2, 'C': 1, 'T': 2, 'G': 0, 'N': 1, "default": 6},
                6: {'A': 3, 'C': 1, 'T': 2, 'G': 0, 'N': 0, "default": 6},
            },
    },
    "three": {
            "my_sample": {
                0: {'A': 1, 'C': 0, 'T': 0, 'G': 0, 'N': 0},
            },
            "my_other_sample": {
                0: {'A': 0, 'C': 0, 'T': 0, 'G': 0, 'N': 1},
            },
            "total": {
                0: {'A': 1, 'C': 0, 'T': 0, 'G': 0, 'N': 1, "default": 2},
            }
    },
}


# TODO Test expected results for max, min, mean, median
class TestGoldilocksRegression_NucleotideCounter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.g = Goldilocks(NucleotideCounterStrategy(["A","C","G","T","N"]), sequence_data, length=3, stride=1)

        # 29 regions * 5 bases * (2+1) samples (two samples + total)
        cls.EXPECTED_REGION_COUNT = 29*5*3

        # Each region gets an additional counter in its total key (total-default)
        cls.EXPECTED_COUNTERS_COUNT = cls.EXPECTED_REGION_COUNT + 29

    def test_group_track_counts_contents(self):
        """Ensure group_counts held by region metadata for each group-track
        combination (including the total-default group-track) match the
        expected number of bases.
        This test is somewhat cheating in that it fetches region metadata from
        the regions dictionary."""

        number_comparisons = 0
        for group in self.g.group_counts:
            for track in self.g.group_counts[group]:
                for region_i, value in enumerate(self.g.group_counts[group][track]):
                    # Get this region_i's chrom and ichr from the region data
                    chrom = self.g.regions[region_i]["chr"]
                    ichr = self.g.regions[region_i]["ichr"]
                    self.assertEqual(EXPECTED_REGIONS[chrom][group][ichr][track], value)

                    number_comparisons += 1
                    ichr += 1
        self.assertEqual(self.EXPECTED_COUNTERS_COUNT, number_comparisons)

    def test_group_track_bucket_contents(self):
        """Check that regions appear in the correct group_buckets for each
        group-track combination (including the total-default group-track).
        The test is somewhat of a cheat in that it assumes the contents of the
        group_counts counters are correct as tested in
        test_group_track_counts_contents."""

        number_comparisons = 0
        for group in self.g.group_buckets:
            for track in self.g.group_buckets[group]:
                for bucket in self.g.group_buckets[group][track]:
                    for region_id in self.g.group_buckets[group][track][bucket]:
                        self.assertEqual(self.g.group_counts[group][track][region_id], bucket)
                        number_comparisons += 1
        self.assertEqual(self.EXPECTED_COUNTERS_COUNT, number_comparisons)


if __name__ == '__main__':
    unittest.main()
