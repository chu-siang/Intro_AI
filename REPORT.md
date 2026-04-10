# Routing System Report

## Summary

This repository now presents the Hsinchu OSM route-finding implementation as a maintainable engineering project. The search entry points still expose the same public API, but the internal structure has been cleaned up so graph loading, heuristic loading, and path reconstruction live in one shared module instead of being duplicated across five scripts.

## Implementation Changes

- Moved shared graph parsing and heuristic caching into [routing_core.py](./routing_core.py).
- Rewrote [bfs.py](./bfs.py), [dfs.py](./dfs.py), [ucs.py](./ucs.py), [astar.py](./astar.py), and [astar_time.py](./astar_time.py) as stable wrappers with no debug-print side effects.
- Added [routing_cli.py](./routing_cli.py) for repeatable command-line execution.
- Added [tests/test_routing.py](./tests/test_routing.py) for regression coverage.
- Added [.gitignore](./.gitignore) to keep generated files and cache directories out of the repo surface.

## Behavior Notes

- BFS still optimizes hop count, not weighted distance.
- DFS still returns the first legal depth-first route, which can be far from optimal.
- UCS and A* return the same shortest-distance values on the published benchmark cases.
- A* Time uses travel time as edge cost and `straight_line_distance / global_max_speed` as an admissible heuristic.

## Validation Approach

The repository supports two validation paths:

```bash
uv run python -m unittest discover -s tests -v
uv run python grader/grade.py
```

The test suite checks legal paths, path-cost consistency, shortest-distance parity, fastest-time parity, and the `start == end` contract. The grader remains available as a compatibility harness for the published benchmark cases.

## Operational Recommendation

Use [README.md](./README.md) as the source of truth for setup, execution, and testing. `REPORT.md` should stay focused on architecture and validation rather than screenshots or submission instructions.
