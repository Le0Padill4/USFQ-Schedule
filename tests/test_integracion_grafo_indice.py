import unittest

from domain.course_index.course_index import CourseIndex
from domain.curriculum_graph import CourseGraph, GraphError
from domain.integration.eligibility import eligible_course_records


class GraphIndexIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.graph = CourseGraph()
        self.index = CourseIndex()
        for code in ('SYN-A', 'SYN-B', 'SYN-C'):
            self.graph.add_course(code, prerequisites_known=code != 'SYN-C')
            self.index.add(code, {'code': code})
        self.graph.add_prerequisite('SYN-A', 'SYN-B')

    def test_eligible_records_follow_prerequisites_and_exclude_unknown(self):
        self.assertEqual(eligible_course_records(self.graph, self.index, []),
                         (('SYN-A', {'code': 'SYN-A'}),))
        self.assertEqual(eligible_course_records(self.graph, self.index, ['SYN-A']),
                         (('SYN-B', {'code': 'SYN-B'}),))
        self.graph.check_invariants()
        self.index.assert_valid()

    def test_missing_eligible_record_fails_without_mutation(self):
        self.index.remove('SYN-B')
        before = self.graph.snapshot()
        with self.assertRaises(KeyError):
            eligible_course_records(self.graph, self.index, ['SYN-A'])
        self.assertEqual(self.graph.snapshot(), before)
        self.assertEqual(len(self.index), 2)
        self.index.assert_valid()

    def test_unknown_passed_course_is_rejected(self):
        with self.assertRaises(GraphError):
            eligible_course_records(self.graph, self.index, ['SYN-MISSING'])


if __name__ == '__main__':
    unittest.main()
