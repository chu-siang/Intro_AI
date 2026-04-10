"""Published benchmark specification for the local compatibility validator."""

SECTIONS = (
    {
        "qid": "q1",
        "label": "Part 1 BFS",
        "func": "bfs",
        "public_max": 5.0,
        "private_max": 0.0,
        "public_mode": "valid_path",
        "private_mode": "valid_path_legal",
    },
    {
        "qid": "q2",
        "label": "Part 2 DFS",
        "func": "dfs",
        "public_max": 5.0,
        "private_max": 0.0,
        "public_mode": "dfs_basic",
        "private_mode": "dfs_legal_cost",
    },
    {
        "qid": "q3",
        "label": "Part 3 UCS",
        "func": "ucs",
        "public_max": 5.0,
        "private_max": 0.0,
        "public_mode": "shortest_distance",
        "private_mode": "shortest_distance_legal",
    },
    {
        "qid": "q4",
        "label": "Part 4 A*",
        "func": "astar",
        "public_max": 5.0,
        "private_max": 0.0,
        "public_mode": "astar_distance_parity",
        "private_mode": "astar_distance_parity_legal",
    },
    {
        "qid": "q5",
        "label": "Part 5 A* Time",
        "func": "astar_time",
        "public_max": 5.0,
        "private_max": 0.0,
        "public_mode": "fastest_time",
        "private_mode": "fastest_time",
    },
)

PUBLIC_CASES = [
    ("case1", 2773409914, 1079387396),
    ("case2", 426882161, 1737223506),
    ("case3", 1718165260, 8513026827),
]

PRIVATE_CASES = []

EXPECTED = {
    "public": {
        "q3": {
            "case1": 4894.677,
            "case2": 4101.559,
            "case3": 13905.072,
        },
        "q4": {
            "case1": 4894.677,
            "case2": 4101.559,
            "case3": 13905.072,
        },
    },
    "private": {},
}

EPS = 1e-2
RUNTIME_LIMIT_SEC = 30.0
