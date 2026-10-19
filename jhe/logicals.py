"""Minimum weight logical operators.

An X-type logical operator is a set of data qubits that overlaps every stabilizer on an even number of qubits and
has odd size (Z-type operators are the same sets, since the code is self-dual). For d <= 9 every minimum weight
logical operator is found by enumerating the whole logical coset with the small C program in enum/enum.c. For larger
d the CP-SAT solver of OR-Tools is used to decide whether a minimum weight logical operator with given properties
exists."""
import json
import subprocess
from pathlib import Path

from ortools.sat.python import cp_model

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
ENUM_SRC = ROOT / "enum" / "enum.c"
ENUM_BIN = ROOT / "enum" / "enum"


def _enum_binary():
    if not ENUM_BIN.exists() or ENUM_BIN.stat().st_mtime < ENUM_SRC.stat().st_mtime:
        subprocess.run(["cc", "-O2", "-o", str(ENUM_BIN), str(ENUM_SRC)], check=True)
    return ENUM_BIN


def enumerate_min_weight(lat):
    """All minimum weight logical operators of the lattice (needs at most 64 data qubits), by enumerating the
    coset seed + span(stabilizers), where the seed is the bottom row of data qubits."""
    n = len(lat.xy)
    assert n <= 64, "the enumerator stores qubit sets in 64-bit words"
    masks = [sum(1 << q for q in f["qs"]) for f in lat.faces]
    seed = sum(1 << q for q, (x, y) in lat.xy.items() if y == 0)
    assert all(bin(seed & m).count("1") % 2 == 0 for m in masks) and bin(seed).count("1") % 2 == 1
    inp = f"{len(masks)} {seed}\n" + "\n".join(map(str, masks)) + "\n"
    out = subprocess.run([str(_enum_binary())], input=inp, capture_output=True, text=True, check=True).stdout.split()
    w, count = int(out[0]), int(out[1])
    ops = [frozenset(q for q in range(n) if int(m) >> q & 1) for m in out[2:]]
    assert len(ops) == count
    return w, ops


def load_min_weight(d):
    """Cached result of enumerate_min_weight for d = 7 or 9 (written by checks/enumerate_logicals.py)."""
    M = json.loads((DATA / f"minlog_d{d}.json").read_text())
    return M["minw"], [frozenset(o) for o in M["ops"]]


class LogicalModel:
    """CP-SAT model whose solutions are the logical operators of weight exactly `weight` (default d)."""

    def __init__(self, lat, weight=None):
        self.lat = lat
        self.m = cp_model.CpModel()
        self.x = {q: self.m.NewBoolVar(f"x{q}") for q in lat.xy}
        for i, f in enumerate(lat.faces):
            k = self.m.NewIntVar(0, len(f["qs"]) // 2, f"k{i}")
            self.m.Add(sum(self.x[q] for q in f["qs"]) == 2 * k)
        self.m.Add(sum(self.x.values()) == (lat.d if weight is None else weight))

    def solve(self, time_limit=600, workers=8):
        """Returns (feasible, status name, solution as a frozenset or None). Raises if the solver could not
        decide within the time limit, so that an undecided instance is never counted as infeasible."""
        s = cp_model.CpSolver()
        s.parameters.max_time_in_seconds = time_limit
        s.parameters.num_workers = workers
        r = s.Solve(self.m)
        name = s.StatusName(r)
        if r in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return True, name, frozenset(q for q, v in self.x.items() if s.Value(v))
        if r == cp_model.INFEASIBLE:
            return False, name, None
        raise RuntimeError(f"CP-SAT did not decide the instance (status {name})")


def exists(lat, contains=(), excludes=(), weight=None):
    """Is there a logical operator of weight d (or `weight`) containing `contains` and avoiding `excludes`?
    Returns (answer, solution or None)."""
    lm = LogicalModel(lat, weight)
    for q in contains:
        lm.m.Add(lm.x[q] == 1)
    for q in excludes:
        lm.m.Add(lm.x[q] == 0)
    ok, _, sol = lm.solve()
    return ok, sol
