import random
import unittest

from domain.course_index.avl import CourseAVL


class CourseAVLTests(unittest.TestCase):
    def test_rotations_and_sorted_output(self):
        for keys in ([3, 2, 1], [1, 2, 3], [3, 1, 2], [1, 3, 2], range(100)):
            index = CourseAVL()
            for key in keys:
                index.put(key, str(key))
                index.assert_valid()
            self.assertEqual(list(index.range_items(0, 100)),
                             [(key, str(key)) for key in sorted(keys)])

    def test_duplicate_range_and_missing(self):
        index = CourseAVL()
        index.put(("202610", "CMP", "123"), 1)
        index.put(("202610", "CMP", "123"), 2)
        self.assertEqual(len(index), 1)
        self.assertEqual(index.get(("202610", "CMP", "123")), 2)
        self.assertEqual(len(list(index.range_items(("202610", "CMP", "123"),
                                                    ("202610", "CMP", "123")))), 1)
        with self.assertRaises(KeyError):
            index.get(("202610", "CMP", "999"))
        with self.assertRaises(ValueError):
            index.range_items(("z",), ("a",))
        index.delete(("202610", "CMP", "123"))
        with self.assertRaises(KeyError):
            index.delete(("202610", "CMP", "123"))
        index.assert_valid()

    def test_random_operations_against_dict(self):
        rng = random.Random(3857)
        index, reference = CourseAVL(), {}
        for _ in range(5000):
            key = rng.randrange(250)
            action = rng.randrange(3)
            if action == 0:
                value = rng.randrange(10000)
                index.put(key, value)
                reference[key] = value
            elif action == 1:
                if key in reference:
                    index.delete(key)
                    del reference[key]
                else:
                    with self.assertRaises(KeyError):
                        index.delete(key)
            else:
                lo, hi = sorted((key, rng.randrange(250)))
                expected = sorted((k, v) for k, v in reference.items() if lo <= k <= hi)
                self.assertEqual(list(index.range_items(lo, hi)), expected)
            self.assertEqual(len(index), len(reference))
            index.assert_valid()
        for key, value in reference.items():
            self.assertEqual(index.get(key), value)


if __name__ == '__main__':
    unittest.main()
