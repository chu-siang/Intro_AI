#!/usr/bin/env python3
"""Local compatibility validator for the published benchmark cases."""

from __future__ import annotations

import argparse
import importlib
import json
import os
import sys
import time
from typing import Callable, Dict, List, Tuple

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from grader.scoring import CheckResult, score_scope
from grader.spec import PRIVATE_CASES, SECTIONS

Result = Tuple[List[int], float, int]


def _load_functions() -> Dict[str, Callable[[int, int], Result]]:
    modules = {
        "bfs": ("bfs", "bfs"),
        "dfs": ("dfs", "dfs"),
        "ucs": ("ucs", "ucs"),
        "astar": ("astar", "astar"),
        "astar_time": ("astar_time", "astar_time"),
    }
    loaded = {}
    for key, (mod_name, fn_name) in modules.items():
        mod = importlib.import_module(mod_name)
        loaded[key] = getattr(mod, fn_name)
    return loaded


def _private_scores(
    funcs: Dict[str, Callable[[int, int], Result]],
    public_only: bool,
) -> Dict[str, List[CheckResult]]:
    results: Dict[str, List[CheckResult]] = {}
    private_enabled = bool(PRIVATE_CASES) and not public_only
    private_grouped = score_scope(funcs, "private") if private_enabled else {}
    for section in SECTIONS:
        if not private_enabled:
            results[section["qid"]] = [
                CheckResult(
                    name=f"{section['label']} private tests (not included in release)",
                    points=0.0,
                    max_points=float(section["private_max"]),
                    passed=False,
                    detail="private tests are not included in this release",
                )
            ]
            continue
        results[section["qid"]] = private_grouped[section["qid"]]
    return results


def _run(public_only: bool) -> Tuple[str, Dict[str, List[CheckResult]], Dict[str, List[CheckResult]], Dict[str, float]]:
    fatal_error = ""
    public_grouped: Dict[str, List[CheckResult]] = {}
    private_grouped: Dict[str, List[CheckResult]] = {}
    try:
        funcs = _load_functions()
        public_grouped = score_scope(funcs, "public")
        private_grouped = _private_scores(funcs, public_only)
    except Exception as exc:  # pragma: no cover
        fatal_error = f"{type(exc).__name__}: {exc}"

    required_score = 0.0
    required_max = 0.0
    for section in SECTIONS:
        qid = section["qid"]
        required_score += sum(c.points for c in public_grouped.get(qid, [])) + sum(c.points for c in private_grouped.get(qid, []))
        required_max += sum(c.max_points for c in public_grouped.get(qid, [])) + sum(c.max_points for c in private_grouped.get(qid, []))
    totals = {"required_score": required_score, "required_max": required_max}
    return fatal_error, public_grouped, private_grouped, totals


def _print_human(
    fatal_error: str,
    public_grouped: Dict[str, List[CheckResult]],
    private_grouped: Dict[str, List[CheckResult]],
    totals: Dict[str, float],
) -> None:
    def _fmt_score(value: float) -> str:
        return str(int(round(value)))

    start = time.localtime()[1:6]
    print("Starting on %d-%d at %d:%02d:%02d" % start)

    for section in SECTIONS:
        public_checks = public_grouped.get(section["qid"], [])
        private_checks = private_grouped.get(section["qid"], [])
        q_points = sum(c.points for c in public_checks) + sum(c.points for c in private_checks)
        q_max = sum(c.max_points for c in public_checks) + sum(c.max_points for c in private_checks)
        print(f"\n{section['label']}")
        print("=" * len(section["label"]))
        print(f"*** Public tests ({_fmt_score(section['public_max'])} pts)")
        for check in public_checks:
            status = "PASS" if check.passed else "FAIL"
            print(f"***   [{status}] {check.name}: {_fmt_score(check.points)}/{_fmt_score(check.max_points)}")
            if check.detail != "ok":
                print(f"***   detail: {check.detail}")
        print(f"*** Private tests ({_fmt_score(section['private_max'])} pts)")
        for check in private_checks:
            status = "PASS" if check.passed else "FAIL"
            print(f"***   [{status}] {check.name}: {_fmt_score(check.points)}/{_fmt_score(check.max_points)}")
            if check.detail != "ok":
                print(f"***   detail: {check.detail}")
        print(f"\n### {section['label']}: {_fmt_score(q_points)}/{_fmt_score(q_max)} ###\n")

    if fatal_error:
        print("*** FAIL: Exception raised: %s" % fatal_error)

    print("\nFinished at %d:%02d:%02d" % time.localtime()[3:6])
    print("\nProvisional grades\n==================")
    for section in SECTIONS:
        q_points = sum(c.points for c in public_grouped.get(section["qid"], [])) + sum(c.points for c in private_grouped.get(section["qid"], []))
        q_max = sum(c.max_points for c in public_grouped.get(section["qid"], [])) + sum(c.max_points for c in private_grouped.get(section["qid"], []))
        print(f"{section['label']}: {_fmt_score(q_points)}/{_fmt_score(q_max)}")
    print("------------------")
    print(f"Total: {_fmt_score(totals['required_score'])}/{_fmt_score(totals['required_max'])}")
    print(
        """
Your grades are NOT yet registered.  To register your grades, make sure
to follow your instructor's guidelines to receive credit on your project.
"""
    )


def _print_json(
    fatal_error: str,
    public_grouped: Dict[str, List[CheckResult]],
    private_grouped: Dict[str, List[CheckResult]],
    totals: Dict[str, float],
) -> None:
    payload = {
        "fatal_error": fatal_error,
        "total_score": round(totals["required_score"], 2),
        "max_score": round(totals["required_max"], 2),
        "sections": {},
    }
    for section in SECTIONS:
        payload["sections"][section["qid"]] = {
            "label": section["label"],
            "public": [
                {
                    "name": c.name,
                    "points": c.points,
                    "max_points": c.max_points,
                    "passed": c.passed,
                    "detail": c.detail,
                }
                for c in public_grouped.get(section["qid"], [])
            ],
            "private": [
                {
                    "name": c.name,
                    "points": c.points,
                    "max_points": c.max_points,
                    "passed": c.passed,
                    "detail": c.detail,
                }
                for c in private_grouped.get(section["qid"], [])
            ],
        }
    print(json.dumps(payload, indent=2, ensure_ascii=True))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local routing compatibility validator.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")
    parser.add_argument(
        "--public-only",
        action="store_true",
        help="Run only the published checks.",
    )
    args = parser.parse_args()

    fatal_error, public_grouped, private_grouped, totals = _run(args.public_only)
    if args.json:
        _print_json(fatal_error, public_grouped, private_grouped, totals)
    else:
        _print_human(fatal_error, public_grouped, private_grouped, totals)
    raise SystemExit(1 if fatal_error else 0)


if __name__ == "__main__":
    main()
