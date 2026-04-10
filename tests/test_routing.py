from __future__ import annotations

import math
import unittest

from astar import astar
from astar_time import astar_time
from bfs import bfs
from dfs import dfs
from grader.path_metrics import load_edge_distance, load_edge_time, path_cost, shortest_travel_time
from ucs import ucs

PUBLIC_CASES = [
    (2773409914, 1079387396),
    (426882161, 1737223506),
    (1718165260, 8513026827),
]

EXPECTED_DISTANCE = {
    (2773409914, 1079387396): 4894.677,
    (426882161, 1737223506): 4101.559,
    (1718165260, 8513026827): 13905.072,
}


class RoutingAlgorithmTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.edge_distance = load_edge_distance()
        cls.edge_time = load_edge_time()

    def assert_legal_path(self, path: list[int], start: int, end: int) -> None:
        self.assertTrue(path, "path must not be empty")
        self.assertEqual(path[0], start)
        self.assertEqual(path[-1], end)

    def test_bfs_returns_legal_paths(self) -> None:
        for start, end in PUBLIC_CASES:
            with self.subTest(start=start, end=end):
                path, distance, visited = bfs(start, end)
                self.assert_legal_path(path, start, end)
                legal, actual = path_cost(path, self.edge_distance)
                self.assertTrue(legal)
                self.assertAlmostEqual(actual, distance, places=2)
                self.assertGreaterEqual(visited, 1)

    def test_dfs_returns_legal_paths(self) -> None:
        for start, end in PUBLIC_CASES:
            with self.subTest(start=start, end=end):
                path, distance, visited = dfs(start, end)
                self.assert_legal_path(path, start, end)
                legal, actual = path_cost(path, self.edge_distance)
                self.assertTrue(legal)
                self.assertAlmostEqual(actual, distance, places=2)
                self.assertGreaterEqual(visited, 1)

    def test_ucs_matches_expected_shortest_distance(self) -> None:
        for start, end in PUBLIC_CASES:
            with self.subTest(start=start, end=end):
                path, distance, visited = ucs(start, end)
                self.assert_legal_path(path, start, end)
                self.assertAlmostEqual(distance, EXPECTED_DISTANCE[(start, end)], places=2)
                self.assertGreaterEqual(visited, 1)

    def test_astar_matches_ucs_distance(self) -> None:
        for start, end in PUBLIC_CASES:
            with self.subTest(start=start, end=end):
                apath, adistance, avisited = astar(start, end)
                upath, udistance, _ = ucs(start, end)
                self.assert_legal_path(apath, start, end)
                self.assert_legal_path(upath, start, end)
                self.assertAlmostEqual(adistance, udistance, places=2)
                self.assertAlmostEqual(adistance, EXPECTED_DISTANCE[(start, end)], places=2)
                self.assertGreaterEqual(avisited, 1)

    def test_astar_time_matches_shortest_travel_time(self) -> None:
        for start, end in PUBLIC_CASES:
            with self.subTest(start=start, end=end):
                path, travel_time, visited = astar_time(start, end)
                self.assert_legal_path(path, start, end)
                legal, actual = path_cost(path, self.edge_time)
                self.assertTrue(legal)
                self.assertAlmostEqual(actual, travel_time, places=2)
                self.assertAlmostEqual(shortest_travel_time(start, end), travel_time, places=2)
                self.assertGreaterEqual(visited, 1)

    def test_start_equals_end_contract(self) -> None:
        start = PUBLIC_CASES[0][0]
        for func in (bfs, dfs, ucs, astar, astar_time):
            with self.subTest(function=func.__name__):
                path, cost, visited = func(start, start)
                self.assertEqual(path, [start])
                self.assertTrue(math.isclose(cost, 0.0))
                self.assertGreaterEqual(visited, 1)


if __name__ == "__main__":
    unittest.main()
