"""Differential check of the index only, not of the complete schedule engine."""
import random
import unittest

from domain.course_index.course_index import CourseIndex
from reference.course_index_slow import SlowCourseIndex


def outcome(index, operation, args):
    try:
        value = getattr(index, operation)(*args)
        if operation == 'range_items':
            value = list(value)
        return ('ok', value)
    except (KeyError, ValueError) as error:
        return ('error', type(error).__name__)


class CourseReferenceTests(unittest.TestCase):
    def test_ten_thousand_list_reference_operations(self):
        rng = random.Random(20261125)
        fast, slow = CourseIndex(), SlowCourseIndex()
        for step in range(10000):
            code = f'X {rng.randrange(250):04}'
            operation = rng.choice(('add', 'get', 'remove', 'range_items'))
            if operation == 'add':
                args = (code, step)
            elif operation == 'range_items':
                other = f'X {rng.randrange(250):04}'
                args = (code, other)  # Includes inverted intervals.
            else:
                args = (code,)
            self.assertEqual(outcome(fast, operation, args),
                             outcome(slow, operation, args), f'step {step}')
            self.assertEqual(len(fast), len(slow))
            fast.assert_valid()
        self.assertEqual(list(fast.range_items('X 0000', 'X 9999')),
                         list(slow.range_items('X 0000', 'X 9999')))


if __name__ == '__main__':
    unittest.main()
