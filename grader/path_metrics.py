"""Shared graph metric helpers for grader checks."""

from __future__ import annotations

import csv
import heapq
import math
from typing import Dict, List, Tuple

_edge_distance: Dict[Tuple[int, int], float] | None = None
_edge_time: Dict[Tuple[int, int], float] | None = None
_time_graph: Dict[int, List[Tuple[int, float]]] | None = None


def load_edge_distance() -> Dict[Tuple[int, int], float]:
    _load_metrics()
    return _edge_distance or {}


def load_edge_time() -> Dict[Tuple[int, int], float]:
    _load_metrics()
    return _edge_time or {}


def path_cost(path: List[int], edge_cost: Dict[Tuple[int, int], float]) -> Tuple[bool, float]:
    total = 0.0
    for u, v in zip(path[:-1], path[1:]):
        cost = edge_cost.get((u, v))
        if cost is None:
            return False, math.inf
        total += cost
    return True, total


def shortest_travel_time(start: int, end: int) -> float:
    _load_metrics()
    graph = _time_graph or {}
    heap: List[Tuple[float, int]] = [(0.0, start)]
    best = {start: 0.0}

    while heap:
        curr_time, node = heapq.heappop(heap)
        if curr_time > best.get(node, math.inf):
            continue
        if node == end:
            return curr_time
        for neighbor, edge_time in graph.get(node, []):
            next_time = curr_time + edge_time
            if next_time < best.get(neighbor, math.inf):
                best[neighbor] = next_time
                heapq.heappush(heap, (next_time, neighbor))

    return math.inf


def _load_metrics() -> None:
    global _edge_distance, _edge_time, _time_graph
    if _edge_distance is not None and _edge_time is not None and _time_graph is not None:
        return

    edge_distance: Dict[Tuple[int, int], float] = {}
    edge_time: Dict[Tuple[int, int], float] = {}
    time_graph: Dict[int, List[Tuple[int, float]]] = {}

    with open("edges.csv", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            u = int(row["start"])
            v = int(row["end"])
            distance = float(row["distance"])
            speed_kmh = float(row["speed limit"])
            speed_mps = speed_kmh * 1000.0 / 3600.0
            if speed_mps <= 0.0:
                continue

            travel_time = distance / speed_mps
            uv = (u, v)

            old_distance = edge_distance.get(uv)
            if old_distance is None or distance < old_distance:
                edge_distance[uv] = distance

            old_time = edge_time.get(uv)
            if old_time is None or travel_time < old_time:
                edge_time[uv] = travel_time

    for (u, v), travel_time in edge_time.items():
        time_graph.setdefault(u, []).append((v, travel_time))
        time_graph.setdefault(v, [])

    _edge_distance = edge_distance
    _edge_time = edge_time
    _time_graph = time_graph
