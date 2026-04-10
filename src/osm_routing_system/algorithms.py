"""Public routing algorithm entry points."""

from __future__ import annotations

from .routing_core import (
    a_star_distance_search,
    a_star_time_search,
    bfs_search,
    dfs_search,
    uniform_cost_search,
)

Result = tuple[list[int], float, int]


def bfs(start: int, end: int) -> Result:
    """Return a breadth-first path between two nodes."""
    result = bfs_search(start, end)
    return result.path, result.cost, result.visited


def dfs(start: int, end: int) -> Result:
    """Return a depth-first path between two nodes."""
    result = dfs_search(start, end)
    return result.path, result.cost, result.visited


def ucs(start: int, end: int) -> Result:
    """Return the minimum-distance path between two nodes."""
    result = uniform_cost_search(start, end)
    return result.path, result.cost, result.visited


def astar(start: int, end: int) -> Result:
    """Return the minimum-distance path using A* search."""
    result = a_star_distance_search(start, end)
    return result.path, result.cost, result.visited


def astar_time(start: int, end: int) -> Result:
    """Return the minimum-travel-time path using A* search."""
    result = a_star_time_search(start, end)
    return result.path, result.cost, result.visited
