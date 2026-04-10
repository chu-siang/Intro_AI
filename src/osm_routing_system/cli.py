"""Command-line interface for running routing algorithms."""

from __future__ import annotations

import argparse
import json
import time
from collections.abc import Callable

from .algorithms import astar, astar_time, bfs, dfs, ucs

Result = tuple[list[int], float, int]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run routing algorithms on the bundled OSM graph.")
    parser.add_argument("algorithm", choices=["bfs", "dfs", "ucs", "astar", "astar_time"])
    parser.add_argument("start", type=int, help="Start node ID")
    parser.add_argument("end", type=int, help="End node ID")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable output.",
    )
    parser.add_argument(
        "--show-path",
        action="store_true",
        help="Include the full path in text output.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    algorithms: dict[str, Callable[[int, int], Result]] = {
        "bfs": bfs,
        "dfs": dfs,
        "ucs": ucs,
        "astar": astar,
        "astar_time": astar_time,
    }

    started = time.perf_counter()
    path, cost, visited = algorithms[args.algorithm](args.start, args.end)
    duration = time.perf_counter() - started

    payload = {
        "algorithm": args.algorithm,
        "start": args.start,
        "end": args.end,
        "cost": cost,
        "visited": visited,
        "path_nodes": len(path),
        "runtime_seconds": duration,
    }

    if args.json:
        payload["path"] = path
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return

    print(f"algorithm: {args.algorithm}")
    print(f"start: {args.start}")
    print(f"end: {args.end}")
    print(f"cost: {cost:.6f}")
    print(f"visited: {visited}")
    print(f"path_nodes: {len(path)}")
    print(f"runtime_seconds: {duration:.6f}")
    if args.show_path:
        print(f"path: {path}")


if __name__ == "__main__":
    main()
