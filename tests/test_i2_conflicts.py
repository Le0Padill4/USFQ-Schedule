import unittest
from domain.course_index.conflicts import Interval, conflicts, overlaps


class ConflictsTests(unittest.TestCase):
    def test_half_open_and_days(self):
        a = Interval(0, 60, 120)
        self.assertFalse(overlaps(a, Interval(0, 120, 180)))
        self.assertTrue(overlaps(a, Interval(0, 119, 180)))
        self.assertTrue(overlaps(a, Interval(0, 60, 120)))
        self.assertFalse(overlaps(a, Interval(1, 60, 120)))
        self.assertTrue(overlaps(Interval(6, 0, 1440), Interval(6, 1439, 1440)))

    def test_collections_and_generators(self):
        a = [Interval(0, 60, 120), Interval(2, 60, 120)]
        b = [Interval(1, 60, 120), Interval(2, 90, 150)]
        self.assertTrue(conflicts(iter(a), iter(b)))
        self.assertFalse(conflicts(a, []))
        self.assertFalse(conflicts([], b))

    def test_invalid(self):
        for value in [(-1, 1, 2), (7, 1, 2), (0, 1, 1), (0, -1, 2),
                      (0, 1, 1441), (True, 1, 2), (0, 1.0, 2)]:
            with self.assertRaises(ValueError):
                Interval(*value)


if __name__ == '__main__':
    unittest.main()
