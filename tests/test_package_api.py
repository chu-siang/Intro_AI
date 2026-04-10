from __future__ import annotations

import unittest

from osm_routing_system import astar, astar_time, bfs, dfs, ucs


class PackageApiTests(unittest.TestCase):
    def test_package_exports_expected_algorithms(self) -> None:
        start = 2773409914
        end = 1079387396

        for func in (bfs, dfs, ucs, astar, astar_time):
            with self.subTest(function=func.__name__):
                path, cost, visited = func(start, end)
                self.assertTrue(path)
                self.assertEqual(path[0], start)
                self.assertEqual(path[-1], end)
                self.assertGreaterEqual(cost, 0.0)
                self.assertGreaterEqual(visited, 1)
