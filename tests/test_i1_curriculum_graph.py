"""BDD/TDD del grafo de I1; solo unittest y fixtures sintéticos."""
import random
import unittest

from domain.curriculum_graph import CourseGraph, GraphError
from i1_graph_reference import ListGraph


class CourseGraphTests(unittest.TestCase):
    def graph(self):
        graph = CourseGraph()
        for code in ("D", "C", "B", "A", "Z"):
            graph.add_course(code, prerequisites_known=True)
        for edge in (("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")):
            graph.add_prerequisite(*edge)
        return graph

    def assert_error(self, code, operation):
        with self.assertRaises(GraphError) as error:
            operation()
        self.assertEqual(code, error.exception.code)

    def test_empty(self):
        graph = CourseGraph()
        self.assertEqual((), graph.courses)
        self.assertEqual((), graph.edges)
        self.assertEqual((), graph.topological_order())
        self.assertEqual((), graph.eligible_courses([]))
        graph.check_invariants()

    def test_atomic_cycle_and_self_loop(self):
        graph = self.graph()
        before = graph.snapshot()
        self.assert_error("CYCLE", lambda: graph.add_prerequisite("D", "A"))
        self.assert_error("CYCLE", lambda: graph.add_prerequisite("A", "A"))
        self.assertEqual(before, graph.snapshot())
        graph.check_invariants()

    def test_duplicate_and_unknown(self):
        graph = self.graph()
        before = graph.snapshot()
        self.assertFalse(graph.add_prerequisite("A", "B"))
        self.assert_error("DUPLICATE_COURSE", lambda: graph.add_course("A"))
        self.assert_error("UNKNOWN_COURSE", lambda: graph.add_prerequisite("MISSING", "B"))
        self.assert_error("UNKNOWN_COURSE", lambda: graph.eligible_courses(["MISSING"]))
        self.assert_error("UNKNOWN_COURSE", lambda: graph.bfs("MISSING"))
        self.assertEqual(before, graph.snapshot())

    def test_invalid_codes_and_flags(self):
        graph = CourseGraph()
        for code in ("", " A", "A ", None, 12, True):
            self.assert_error("INVALID_CODE", lambda: graph.add_course(code))
        self.assert_error("INVALID_FLAG", lambda: graph.add_course("A", prerequisites_known=1))
        self.assertEqual((), graph.courses)

    def test_invalid_passed_collections(self):
        graph = self.graph()
        for value in (None, 5, True, "A", b"A", [["A"]]):
            self.assert_error("INVALID_CODE", lambda: graph.eligible_courses(value))
        self.assert_error("INVALID_FLAG", lambda: graph.dependencies("A", transitive=1))

    def test_traversals_and_dependencies(self):
        graph = self.graph()
        self.assertEqual(("A", "B", "C", "D"), graph.bfs("A"))
        self.assertEqual(("A", "B", "D", "C"), graph.dfs("A"))
        self.assertEqual(("B", "C"), graph.dependencies("D", transitive=False))
        self.assertEqual(("A", "B", "C"), graph.dependencies("D"))
        self.assertEqual(("B", "C", "D"), graph.dependents("A"))
        self.assertEqual(("B", "C"), graph.dependents("A", transitive=False))
        self.assertEqual(("Z",), graph.bfs("Z"))
        self.assertEqual((), graph.dependencies("Z"))

    def test_topology_is_deterministic(self):
        first = self.graph()
        second = CourseGraph()
        for code in reversed(first.courses):
            second.add_course(code, prerequisites_known=True)
        for edge in reversed(first.edges):
            second.add_prerequisite(*edge)
        self.assertEqual(("A", "B", "C", "D", "Z"), first.topological_order())
        self.assertEqual(first.snapshot(), second.snapshot())
        self.assertEqual(first.topological_order(), second.topological_order())
        self.assertEqual(first.dfs("A"), second.dfs("A"))

    def test_known_rules_and_and_semantics(self):
        graph = self.graph()
        graph.add_course("UNKNOWN")
        self.assertEqual(("A", "Z"), graph.eligible_courses([]))
        self.assertEqual(("B", "C", "Z"), graph.eligible_courses(["A", "A"]))
        self.assertEqual(("C", "Z"), graph.eligible_courses(["A", "B"]))
        self.assertEqual(("D", "Z"), graph.eligible_courses(["A", "B", "C"]))
        self.assertFalse(graph.rules_known("UNKNOWN"))
        graph.set_rules_known("UNKNOWN", True)
        self.assertIn("UNKNOWN", graph.eligible_courses([]))

    def test_removals_invalidate_dependent_rule_completeness(self):
        graph = self.graph()
        self.assertTrue(graph.remove_prerequisite("A", "B"))
        self.assertFalse(graph.rules_known("B"))
        self.assertNotIn("B", graph.eligible_courses([]))
        self.assertFalse(graph.remove_prerequisite("A", "B"))
        graph.set_rules_known("B", True)
        self.assertIn("B", graph.eligible_courses([]))
        graph.remove_course("C")
        self.assertFalse(graph.rules_known("D"))
        self.assertEqual((("B", "D"),), graph.edges)
        graph.check_invariants()

    def test_views_are_detached_and_invalid_inputs_do_not_mutate(self):
        graph = self.graph()
        old = graph.snapshot()
        self.assert_error("INVALID_FLAG", lambda: graph.set_rules_known("A", 1))
        self.assertEqual(old, graph.snapshot())
        graph.remove_course("A")
        self.assertIn("A", old[0])
        self.assertNotIn("A", graph.courses)

    def test_long_chain_is_iterative(self):
        graph = CourseGraph()
        for index in range(1500):
            graph.add_course(f"SYN-{index:04}", prerequisites_known=True)
            if index:
                graph.add_prerequisite(f"SYN-{index-1:04}", f"SYN-{index:04}")
        self.assertEqual(1500, len(graph.dfs("SYN-0000")))
        self.assertEqual(1499, len(graph.dependencies("SYN-1499")))
        self.assert_error("CYCLE", lambda: graph.add_prerequisite("SYN-1499", "SYN-0000"))
        graph.check_invariants()

    def test_10000_random_operations_against_independent_list_reference(self):
        rng = random.Random(20261125)
        actual, reference = CourseGraph(), ListGraph()
        codes = [f"SYN-{index:02}" for index in range(24)]

        def call(graph, action, a, b, flag, passed):
            try:
                if action == 0:
                    result = graph.add_course(a, prerequisites_known=flag)
                elif action == 1:
                    result = graph.remove_course(a)
                elif action == 2:
                    result = graph.add_prerequisite(a, b)
                elif action == 3:
                    result = graph.remove_prerequisite(a, b)
                elif action == 4:
                    result = graph.set_rules_known(a, flag)
                elif action == 5:
                    result = graph.eligible_courses(passed)
                elif action == 6:
                    result = graph.dependencies(a)
                else:
                    result = graph.topological_order()
                return ("ok", result)
            except (GraphError, ListGraph.Error) as error:
                return ("error", error.code)

        for step in range(10000):
            action = rng.randrange(8)
            a, b = rng.choice(codes + ["", "NO-EXISTE"]), rng.choice(codes)
            flag = rng.choice([True, False])
            passed = rng.sample(codes, rng.randrange(5))
            with self.subTest(step=step, action=action):
                expected = call(reference, action, a, b, flag, passed)
                self.assertEqual(expected, call(actual, action, a, b, flag, passed))
                self.assertEqual(reference.snapshot(), actual.snapshot())
                actual.check_invariants()


if __name__ == "__main__":
    unittest.main()
