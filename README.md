# OSM Routing System

`osm-routing-system` is a compact routing benchmark built on a directed OpenStreetMap road graph for Hsinchu City. It exposes five algorithms over the same dataset:

- `bfs`: breadth-first traversal over hop count
- `dfs`: depth-first traversal
- `ucs`: shortest-path search by distance
- `astar`: shortest-path search by distance with Euclidean heuristics
- `astar_time`: fastest-path search by travel time with an admissible time heuristic

The repository now follows a more standard Python layout:

- `src/osm_routing_system/`: importable package with the main implementation
- top-level scripts such as `routing_cli.py`: compatibility shims so existing commands still work
- `tests/`: regression tests
- `grader/`: released compatibility validator
- `edges.csv`, `heuristic.csv`, `graph.pkl`: bundled data assets

## Repository Layout

- `src/osm_routing_system/routing_core.py`: shared graph loaders and search implementations
- `src/osm_routing_system/algorithms.py`: stable public Python API
- `src/osm_routing_system/cli.py`: command-line runner
- `src/osm_routing_system/generate_report_maps.py`: PNG generation CLI
- `grader/`: compatibility validator for the published benchmark cases
- `tests/`: regression tests
- `generate_report_maps.py`, `route_map.py`: compatibility entry points
- `edges.csv`, `heuristic.csv`, `graph.pkl`: bundled data assets

## Setup

This project targets Python `3.11` and uses `uv` for environment management.

```bash
uv python pin 3.11
uv sync
```

`uv sync` creates `.venv`, installs the package in editable mode, and installs the dependencies declared in [pyproject.toml](./pyproject.toml).

## Run

Run the packaged CLI:

```bash
uv run osm-routing astar 2773409914 1079387396
```

Machine-readable output:

```bash
uv run osm-routing astar_time 2773409914 1079387396 --json
```

The old script entry point still works:

```bash
uv run python routing_cli.py astar 2773409914 1079387396
```

Generate a route PNG with the packaged command:

```bash
uv run osm-routing-render --start 2773409914 --end 1079387396 --algorithm astar
```

## Test

Regression tests:

```bash
uv run python -m unittest discover -s tests -v
```

Compatibility grader:

```bash
uv run python grader/grade.py
```

The `unittest` suite verifies path legality, shortest-distance parity, fastest-time parity, and the `start == end` contract. The grader keeps the published benchmark interface intact.

Static checks:

```bash
uv run ruff check src tests *.py
uv run mypy src
```

## Sample Output

A sample rendered route image is available at [result/astar_map.png](./result/astar_map.png).

![Sample A* route](./result/astar_map.png)

## API Contract

Python API:

```python
from osm_routing_system import astar, astar_time, bfs, dfs, ucs
```

Each algorithm function accepts `(start: int, end: int)` and returns:

```python
(path, cost_or_time, num_visited)
```

- `path`: `list[int]`
- `cost_or_time`: `float`
- `num_visited`: number of expanded nodes

For `bfs`, `dfs`, `ucs`, and `astar`, the cost is total path distance in meters. For `astar_time`, the cost is total travel time in seconds.

## Engineering Notes

- The graph is loaded once and cached process-wide.
- Neighbor ordering follows `edges.csv`, which keeps traversal behavior deterministic.
- `astar_time` uses `straight_line_distance / global_max_speed` as an admissible lower bound on travel time.
- Root-level modules are kept as compatibility shims for the original benchmark interface.

## Known Constraints

- Visualization utilities fetch map tiles over the network at runtime.
- The dataset is fixed and bundled locally; this project does not ingest live OSM updates.
- The benchmark favors correctness and reproducibility over service-style latency engineering.
