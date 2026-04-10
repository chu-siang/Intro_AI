from __future__ import annotations

import csv
import heapq
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from itertools import count
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parent.parent
EDGES_FILE = PROJECT_ROOT / "edges.csv"
HEURISTIC_FILE = PROJECT_ROOT / "heuristic.csv"


@dataclass(frozen=True)
class SearchResult:
    path: list[int]
    cost: float
    visited: int


_distance_graph: dict[int, list[tuple[int, float]]] | None = None
_time_graph: dict[int, list[tuple[int, float]]] | None = None
_heuristics: dict[int, dict[int, float]] | None = None
_max_speed_mps: float | None = None


def load_distance_graph() -> dict[int, list[tuple[int, float]]]:
    _load_edges()
    return _distance_graph or {}


def load_time_graph() -> dict[int, list[tuple[int, float]]]:
    _load_edges()
    return _time_graph or {}


def load_heuristics() -> dict[int, dict[int, float]]:
    global _heuristics
    if _heuristics is not None:
        return _heuristics

    heuristics: dict[int, dict[int, float]] = {}
    with HEURISTIC_FILE.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            node = int(row["node"])
            heuristics[node] = {
                int(goal): float(value)
                for goal, value in row.items()
                if goal != "node" and value
            }

    _heuristics = heuristics
    return heuristics


def max_speed_mps() -> float:
    _load_edges()
    return _max_speed_mps or 0.0


def bfs_search(start: int, end: int) -> SearchResult:
    if start == end:
        return SearchResult([start], 0.0, 1)

    graph = load_distance_graph()
    queue: deque[int] = deque([start])
    parents = {start: (None, 0.0)}
    visited = {start}
    expanded = 0

    while queue:
        node = queue.popleft()
        expanded += 1
        if node == end:
            return reconstruct_path(parents, end, expanded)

        for neighbor, distance in graph.get(node, []):
            if neighbor in visited:
                continue
            visited.add(neighbor)
            parents[neighbor] = (node, distance)
            queue.append(neighbor)

    return SearchResult([], float("inf"), expanded)


def dfs_search(start: int, end: int) -> SearchResult:
    if start == end:
        return SearchResult([start], 0.0, 1)

    graph = load_distance_graph()
    stack: list[tuple[int, int | None, float]] = [(start, None, 0.0)]
    parents: dict[int, tuple[int | None, float]] = {}
    visited: set[int] = set()
    expanded = 0

    while stack:
        node, parent, edge_cost = stack.pop()
        if node in visited:
            continue

        visited.add(node)
        parents[node] = (parent, edge_cost)
        expanded += 1
        if node == end:
            return reconstruct_path(parents, end, expanded)

        for neighbor, distance in reversed(graph.get(node, [])):
            if neighbor not in visited:
                stack.append((neighbor, node, distance))

    return SearchResult([], float("inf"), expanded)


def uniform_cost_search(start: int, end: int) -> SearchResult:
    return best_first_search(
        start,
        end,
        graph=load_distance_graph(),
        heuristic=lambda _: 0.0,
    )


def a_star_distance_search(start: int, end: int) -> SearchResult:
    heuristics = load_heuristics()
    return best_first_search(
        start,
        end,
        graph=load_distance_graph(),
        heuristic=lambda node: heuristics.get(node, {}).get(end, 0.0),
    )


def a_star_time_search(start: int, end: int) -> SearchResult:
    heuristics = load_heuristics()
    top_speed = max_speed_mps()

    def estimate(node: int) -> float:
        if top_speed <= 0.0:
            return 0.0
        return heuristics.get(node, {}).get(end, 0.0) / top_speed

    return best_first_search(
        start,
        end,
        graph=load_time_graph(),
        heuristic=estimate,
    )


def best_first_search(
    start: int,
    end: int,
    graph: dict[int, list[tuple[int, float]]],
    heuristic: Callable[[int], float],
) -> SearchResult:
    if start == end:
        return SearchResult([start], 0.0, 1)

    frontier: list[tuple[float, float, int, int]] = []
    sequence = count()
    heapq.heappush(frontier, (heuristic(start), 0.0, next(sequence), start))

    parents: dict[int, tuple[int | None, float]] = {start: (None, 0.0)}
    best_cost = {start: 0.0}
    closed: set[int] = set()
    expanded = 0

    while frontier:
        _, cost_so_far, _, node = heapq.heappop(frontier)
        if node in closed:
            continue

        closed.add(node)
        expanded += 1
        if node == end:
            return reconstruct_path(parents, end, expanded)

        for neighbor, edge_cost in graph.get(node, []):
            if neighbor in closed:
                continue
            next_cost = cost_so_far + edge_cost
            if next_cost >= best_cost.get(neighbor, float("inf")):
                continue
            best_cost[neighbor] = next_cost
            parents[neighbor] = (node, edge_cost)
            priority = next_cost + heuristic(neighbor)
            heapq.heappush(frontier, (priority, next_cost, next(sequence), neighbor))

    return SearchResult([], float("inf"), expanded)


def reconstruct_path(
    parents: dict[int, tuple[int | None, float]],
    end: int,
    expanded: int,
) -> SearchResult:
    path: list[int] = []
    total_cost = 0.0
    node: int | None = end

    while node is not None:
        path.append(node)
        parent, edge_cost = parents[node]
        total_cost += edge_cost
        node = parent

    path.reverse()
    return SearchResult(path, total_cost, expanded)


def _load_edges() -> None:
    global _distance_graph, _time_graph, _max_speed_mps
    if _distance_graph is not None and _time_graph is not None and _max_speed_mps is not None:
        return

    distance_graph: dict[int, list[tuple[int, float]]] = {}
    time_graph: dict[int, list[tuple[int, float]]] = {}
    top_speed = 0.0

    with EDGES_FILE.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            start = int(row["start"])
            end = int(row["end"])
            distance = float(row["distance"])
            speed_kmh = float(row["speed limit"])
            speed_mps = speed_kmh * 1000.0 / 3600.0

            distance_graph.setdefault(start, []).append((end, distance))
            distance_graph.setdefault(end, [])

            if speed_mps > 0.0:
                time_graph.setdefault(start, []).append((end, distance / speed_mps))
                top_speed = max(top_speed, speed_mps)
            time_graph.setdefault(end, [])

    _distance_graph = distance_graph
    _time_graph = time_graph
    _max_speed_mps = top_speed
