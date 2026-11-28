import random
import unittest

from domain.course_index.nrc_index import NRCIndex


class NRCIndexTests(unittest.TestCase):
    def test_scope_and_duplicate(self):
        index = NRCIndex()
        index.add('202610', '0012', 'a')
        index.add('202620', '0012', 'b')
        index.add('202610', '12', 'c')
        self.assertEqual(index.get('202610', '0012'), 'a')
        self.assertEqual(index.get('202620', '0012'), 'b')
        with self.assertRaises(ValueError):
            index.add('202610', '0012', 'replacement')
        self.assertEqual(index.get('202610', '0012'), 'a')
        self.assertEqual(len(index), 3)
        index.remove('202610', '0012')
        with self.assertRaises(KeyError):
            index.get('202610', '0012')
        self.assertEqual(index.get('202620', '0012'), 'b')
        index.assert_valid()

    def test_invalid(self):
        index = NRCIndex()
        for term, nrc in [('', '1'), ('x', ''), (' x', '1'), ('x', '1 '), (None, '1'), ('x', 1)]:
            with self.assertRaises(ValueError):
                index.add(term, nrc, None)
        self.assertEqual(len(index), 0)
        with self.assertRaises(KeyError):
            index.remove('202610', 'missing')

    def test_random_against_mapping(self):
        rng = random.Random(456)
        index = NRCIndex()
        reference = {}
        for _ in range(2000):
            term, nrc = str(rng.randrange(3)), str(rng.randrange(50)).zfill(3)
            key = term, nrc
            if rng.randrange(2):
                if key in reference:
                    with self.assertRaises(ValueError):
                        index.add(term, nrc, 1)
                else:
                    reference[key] = rng.randrange(1000)
                    index.add(term, nrc, reference[key])
            elif key in reference:
                index.remove(term, nrc)
                del reference[key]
            else:
                with self.assertRaises(KeyError):
                    index.remove(term, nrc)
            index.assert_valid()
            self.assertEqual(len(index), len(reference))
        for (term, nrc), value in reference.items():
            self.assertEqual(index.get(term, nrc), value)


if __name__ == '__main__':
    unittest.main()
