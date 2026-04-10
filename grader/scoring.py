"""Shared grading logic driven by grader.spec."""

from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Callable, Dict, List, Sequence, Tuple

from grader.path_metrics import load_edge_distance, load_edge_time, path_cost, shortest_travel_time
from grader.spec import EPS, EXPECTED, PRIVATE_CASES, PUBLIC_CASES, RUNTIME_LIMIT_SEC, SECTIONS

Result = Tuple[List[int], float, int]


@dataclass
class CheckResult:
    name: str
    points: float
    max_points: float
    passed: bool
    detail: str


def cases_for(scope: str) -> List[Tuple[str, int, int]]:
    if scope == "public":
        return PUBLIC_CASES
    if scope == "private":
        return PRIVATE_CASES
    raise ValueError(f"unknown scope: {scope}")


def score_scope(funcs: Dict[str, Callable[[int, int], Result]], scope: str) -> Dict[str, List[CheckResult]]:
    results: Dict[str, List[CheckResult]] = {}
    for section in SECTIONS:
        result = score_section(funcs, scope, section)
        results[section["qid"]] = [result]
    return results


def score_section(
    funcs: Dict[str, Callable[[int, int], Result]],
    scope: str,
    section: dict,
) -> CheckResult:
    mode_key = f"{scope}_mode"
    max_key = f"{scope}_max"
    mode = section[mode_key]
    max_points = float(section[max_key])
    label = f"{section['label']} {scope} tests"
    passed, detail = run_mode(funcs, scope, section, mode)
    return CheckResult(
        name=label,
        points=max_points if passed else 0.0,
        max_points=max_points,
        passed=passed,
        detail=detail,
    )


def run_mode(
    funcs: Dict[str, Callable[[int, int], Result]],
    scope: str,
    section: dict,
    mode: str,
) -> Tuple[bool, str]:
    cases = cases_for(scope)
    func = funcs[section["func"]]
    expected = EXPECTED.get(scope, {}).get(section["qid"], {})

    if mode == "valid_path":
        return _check_valid_path(func, cases, require_legal=False)
    if mode == "valid_path_legal":
        return _check_valid_path(func, cases, require_legal=True)
    if mode == "dfs_basic":
        return _check_dfs(func, cases, require_legal=False)
    if mode == "dfs_legal_cost":
        return _check_dfs(func, cases, require_legal=True)
    if mode == "shortest_distance":
        return _check_shortest_distance(func, cases, expected, require_legal=False)
    if mode == "shortest_distance_legal":
        return _check_shortest_distance(func, cases, expected, require_legal=True)
    if mode == "astar_distance_parity":
        return _check_astar(funcs, cases, expected, require_legal=False)
    if mode == "astar_distance_parity_legal":
        return _check_astar(funcs, cases, expected, require_legal=True)
    if mode == "fastest_time":
        return _check_fastest_time(func, cases)
    raise ValueError(f"unknown mode: {mode}")


def _validate_result_shape(result: Result, start: int, end: int, allow_empty: bool) -> Tuple[bool, str]:
    if not isinstance(result, tuple) or len(result) != 3:
        return False, "return must be tuple(path, cost, num_visited)"
    path, cost, visited = result
    if not isinstance(path, list):
        return False, "path must be list"
    if not isinstance(cost, (int, float)):
        return False, "cost/time must be number"
    if not isinstance(visited, int):
        return False, "num_visited must be int"
    if visited < 0:
        return False, "num_visited must be non-negative"
    if not allow_empty and not path:
        return False, "empty path"
    if path and (path[0] != start or path[-1] != end):
        return False, "path endpoints mismatch"
    return True, "ok"


def _check_valid_path(
    func: Callable[[int, int], Result],
    cases: Sequence[Tuple[str, int, int]],
    require_legal: bool,
) -> Tuple[bool, str]:
    edge_distance = load_edge_distance() if require_legal else None
    issues: List[str] = []
    t0 = time.perf_counter()
    first = cases[0]
    valid, reason = _validate_result_shape(func(first[1], first[2]), first[1], first[2], allow_empty=True)
    if not valid:
        issues.append(f"interface: {reason}")
    for name, start, end in cases:
        result = func(start, end)
        valid, reason = _validate_result_shape(result, start, end, allow_empty=False)
        path = result[0] if isinstance(result, tuple) and len(result) == 3 else []
        if not valid:
            issues.append(f"{name}: {reason}")
            continue
        if require_legal:
            legal, _ = path_cost(path, edge_distance or {})
            if not legal:
                issues.append(f"{name}: illegal path")
    elapsed = time.perf_counter() - t0
    if elapsed > RUNTIME_LIMIT_SEC:
        issues.append(f"runtime: {elapsed:.4f}s")
    return (len(issues) == 0, "ok" if not issues else " | ".join(issues))


def _check_dfs(
    func: Callable[[int, int], Result],
    cases: Sequence[Tuple[str, int, int]],
    require_legal: bool,
) -> Tuple[bool, str]:
    edge_distance = load_edge_distance() if require_legal else None
    issues: List[str] = []
    t0 = time.perf_counter()
    for name, start, end in cases:
        result = func(start, end)
        valid, reason = _validate_result_shape(result, start, end, allow_empty=False)
        path, cost, visited = result if isinstance(result, tuple) and len(result) == 3 else ([], 0.0, 0)
        if not valid:
            issues.append(f"{name}: {reason}")
            continue
        if visited < 1:
            issues.append(f"{name}: visited must be >= 1")
        if require_legal:
            legal, dist = path_cost(path, edge_distance or {})
            if not legal:
                issues.append(f"{name}: illegal path")
                continue
            if abs(cost - dist) > EPS:
                issues.append(f"{name}: dfs cost mismatch (expected {dist}, got {cost})")
    same = cases[0][1]
    path, cost, visited = func(same, same)
    if not (path == [same] and abs(cost) <= EPS and visited >= 1):
        issues.append(f"start=end failed: path={path}, cost={cost}, visited={visited}")
    elapsed = time.perf_counter() - t0
    if elapsed > RUNTIME_LIMIT_SEC:
        issues.append(f"runtime: {elapsed:.4f}s")
    return (len(issues) == 0, "ok" if not issues else " | ".join(issues))


def _check_shortest_distance(
    func: Callable[[int, int], Result],
    cases: Sequence[Tuple[str, int, int]],
    expected: dict,
    require_legal: bool,
) -> Tuple[bool, str]:
    edge_distance = load_edge_distance() if require_legal else None
    issues: List[str] = []
    t0 = time.perf_counter()
    for name, start, end in cases:
        result = func(start, end)
        valid, reason = _validate_result_shape(result, start, end, allow_empty=require_legal is False)
        path, dist, _ = result if isinstance(result, tuple) and len(result) == 3 else ([], math.inf, 0)
        if not valid:
            issues.append(f"{name}: {reason}")
            continue
        exp = expected[name]
        if abs(dist - exp) > EPS:
            issues.append(f"{name}: expected {exp}, got {dist}")
        if require_legal:
            legal, actual = path_cost(path, edge_distance or {})
            if not legal:
                issues.append(f"{name}: illegal path")
                continue
            if abs(actual - dist) > EPS:
                issues.append(f"{name}: path-distance mismatch (path {actual}, cost {dist})")
    elapsed = time.perf_counter() - t0
    if elapsed > RUNTIME_LIMIT_SEC:
        issues.append(f"runtime: {elapsed:.4f}s")
    return (len(issues) == 0, "ok" if not issues else " | ".join(issues))


def _check_astar(
    funcs: Dict[str, Callable[[int, int], Result]],
    cases: Sequence[Tuple[str, int, int]],
    expected: dict,
    require_legal: bool,
) -> Tuple[bool, str]:
    edge_distance = load_edge_distance() if require_legal else None
    issues: List[str] = []
    t0 = time.perf_counter()
    for name, start, end in cases:
        ares = funcs["astar"](start, end)
        ures = funcs["ucs"](start, end)
        valid, reason = _validate_result_shape(ares, start, end, allow_empty=require_legal is False)
        apath, adist, _ = ares if isinstance(ares, tuple) and len(ares) == 3 else ([], math.inf, 0)
        _, udist, _ = ures if isinstance(ures, tuple) and len(ures) == 3 else ([], math.inf, 0)
        if not valid:
            issues.append(f"{name}: {reason}")
            continue
        exp = expected[name]
        if abs(adist - exp) > EPS:
            issues.append(f"{name}: expected {exp}, got {adist}")
        if abs(adist - udist) > EPS:
            issues.append(f"{name}: astar/ucs mismatch ({adist} vs {udist})")
        if require_legal:
            legal, actual = path_cost(apath, edge_distance or {})
            if not legal:
                issues.append(f"{name}: illegal path")
                continue
            if abs(actual - adist) > EPS:
                issues.append(f"{name}: path-distance mismatch (path {actual}, cost {adist})")
    elapsed = time.perf_counter() - t0
    if elapsed > RUNTIME_LIMIT_SEC:
        issues.append(f"runtime: {elapsed:.4f}s")
    return (len(issues) == 0, "ok" if not issues else " | ".join(issues))


def _check_fastest_time(
    func: Callable[[int, int], Result],
    cases: Sequence[Tuple[str, int, int]],
) -> Tuple[bool, str]:
    edge_time = load_edge_time()
    expected_time = {name: shortest_travel_time(start, end) for name, start, end in cases}
    issues: List[str] = []
    t0 = time.perf_counter()
    for name, start, end in cases:
        result = func(start, end)
        valid, reason = _validate_result_shape(result, start, end, allow_empty=False)
        path, tsec, _ = result if isinstance(result, tuple) and len(result) == 3 else ([], math.inf, 0)
        if not valid:
            issues.append(f"{name}: {reason}")
            continue
        if tsec < 0 or not math.isfinite(tsec):
            issues.append(f"{name}: invalid travel time {tsec}")
            continue
        legal, actual = path_cost(path, edge_time)
        if not legal:
            issues.append(f"{name}: illegal path")
            continue
        if abs(actual - tsec) > EPS:
            issues.append(f"{name}: path-time mismatch (path {actual}, time {tsec})")
        if abs(expected_time[name] - tsec) > EPS:
            issues.append(f"{name}: expected fastest time {expected_time[name]}, got {tsec}")
    elapsed = time.perf_counter() - t0
    if elapsed > RUNTIME_LIMIT_SEC:
        issues.append(f"runtime: {elapsed:.4f}s")
    return (len(issues) == 0, "ok" if not issues else " | ".join(issues))
