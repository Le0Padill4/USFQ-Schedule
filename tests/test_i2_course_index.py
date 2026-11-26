import random
import unittest
from domain.course_index.course_index import CourseIndex


class CourseIndexTests(unittest.TestCase):
    def test_order_lookup_and_duplicates(self):
        index = CourseIndex()
        index.add('MAT 1201', 'mat')
        index.add('CMP 3002', 'cmp')
        index.add('ESP 1001', 'esp')
        self.assertEqual(list(index.range_items('CMP 3002', 'ESP 1001')),
                         [('CMP 3002', 'cmp'), ('ESP 1001', 'esp')])
        with self.assertRaises(ValueError):
            index.add('CMP 3002', 'otro')
        self.assertEqual(index.get('CMP 3002'), 'cmp')
        index.remove('ESP 1001')
        with self.assertRaises(KeyError):
            index.get('ESP 1001')
        self.assertEqual(len(index), 2)
        index.assert_valid()

    def test_invalid_and_reversed(self):
        index = CourseIndex()
        for code in ('', ' a', 'a ', None):
            with self.assertRaises(ValueError):
                index.add(code, None)
        with self.assertRaises(ValueError):
            index.range_items('Z', 'A')
        with self.assertRaises(KeyError):
            index.remove('ABSENT')

    def test_random_against_dict(self):
        rng = random.Random(6789)
        index, expected = CourseIndex(), {}
        for _ in range(2000):
            code = f'X {rng.randrange(200):04}'
            if rng.randrange(2):
                if code in expected:
                    with self.assertRaises(ValueError):
                        index.add(code, 1)
                else:
                    expected[code] = rng.randrange(1000)
                    index.add(code, expected[code])
            elif code in expected:
                index.remove(code)
                del expected[code]
            else:
                with self.assertRaises(KeyError):
                    index.remove(code)
            index.assert_valid()
            self.assertEqual(len(index), len(expected))
        self.assertEqual(list(index.range_items('X 0000', 'X 0199')), sorted(expected.items()))


if __name__ == '__main__':
    unittest.main()
