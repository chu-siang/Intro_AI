"""CLI for generating route PNGs for one or more algorithms."""

from __future__ import annotations

import argparse
import os
from collections.abc import Callable

from .algorithms import astar, astar_time, bfs, dfs, ucs
from .map_renderer import save_route_map_png

Result = tuple[list[int], float, int]
AlgorithmSpec = tuple[str, str, Callable[[int, int], Result], str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate report route maps for one start/end pair."
    )
    parser.add_argument("--start", type=int, required=True, help="Start node ID")
    parser.add_argument("--end", type=int, required=True, help="End node ID")
    parser.add_argument("--output-dir", default="result", help="Directory for generated PNG files")
    parser.add_argument(
        "--algorithm",
        choices=["all", "bfs", "dfs", "ucs", "astar", "astar_time"],
        default="all",
        help="Generate one map only, or all maps (default: all)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    algorithms: dict[str, AlgorithmSpec] = {
        "bfs": ("BFS", "bfs_map.png", bfs, "blue"),
        "dfs": ("DFS", "dfs_map.png", dfs, "green"),
        "ucs": ("UCS", "ucs_map.png", ucs, "violet"),
        "astar": ("A*", "astar_map.png", astar, "red"),
        "astar_time": ("A* Time", "astar_time_map.png", astar_time, "orange"),
    }

    selected: list[AlgorithmSpec]
    if args.algorithm == "all":
        selected = list(algorithms.values())
    else:
        selected = [algorithms[args.algorithm]]

    for label, filename, func, color in selected:
        print(f"[start] {label}: solving path from {args.start} to {args.end}")
        if label == "DFS":
            print(
                "[info] DFS maps may take longer to render because DFS paths often "
                "contain more nodes. This is expected."
            )
        path, cost, visited = func(args.start, args.end)
        if not path:
            print(f"[skip] {label}: empty path")
            continue

        output_file = os.path.join(args.output_dir, filename)
        failed_tiles = save_route_map_png(path, output_file=output_file, route_color=color)
        print(
            f"[done] {label}: path_nodes={len(path)} cost={cost} visited={visited} "
            f"failed_tiles={failed_tiles} output={output_file}"
        )


if __name__ == "__main__":
    main()
