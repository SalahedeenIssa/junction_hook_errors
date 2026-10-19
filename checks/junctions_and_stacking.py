"""Junctions and stacking of hook errors (Introduction and Sec. 4 of the note).

1. No minimum weight logical operator has two junctions (data qubits outside it whose three neighbors are all in it).
2. No minimum weight logical operator contains two disjoint weight-2 hook errors of the schedule, counting the hook
   errors of every stabilizer, corner stabilizers included. (Both representatives of a weight-4 stabilizer's hook
   error are taken into account.) Hence a single minimum weight logical operator can use at most one hook error.

d = 7 and 9 are checked over all enumerated operators and again with CP-SAT; d = 11 with CP-SAT, where the expected
answer is a proof of infeasibility.

As a control, the same search is run for a hypothetical schedule in which every red hexagon has a hook error on its
top-left and bottom-right data qubits, one of the red single-color malign pairs of Fig. 1(a) of Kishony and Fowler.
These do stack: the search finds a minimum weight logical operator containing two of them (by enumeration, up to two
at d = 7 and three at d = 9)."""
import itertools
import sys

import _setup  # noqa: F401
from jhe import Lattice
from jhe.logicals import LogicalModel, load_min_weight


def hook_representatives(lat):
    """(hook error id, pair) for every weight-2 hook error of every stabilizer and each of its representatives."""
    reps = []
    for i, f in enumerate(lat.faces):
        for j, h in enumerate(lat.hook_errors(f)):
            for p in h["pairs"]:
                reps.append(((i, j), frozenset(p)))
    return reps


def stackable(reps):
    """Pairs of representatives of different hook errors with disjoint supports."""
    return [(r1, r2) for r1, r2 in itertools.combinations(reps, 2) if r1[0] != r2[0] and not r1[1] & r2[1]]


def by_enumeration(lat, ops):
    reps = hook_representatives(lat)
    max_junctions = max(len(lat.junctions(L)) for L in ops)
    stacked = sum(1 for L in ops for r1, r2 in stackable([r for r in reps if r[1] <= L]))
    return max_junctions, stacked


def control_representatives(lat):
    return [((i, 0), frozenset((f["lab"]["TL"], f["lab"]["BR"]))) for i, f in enumerate(lat.faces)
            if f["c"] == "r" and f["kind"] == "hex"]


def stacking_model(lat, reps):
    lm = LogicalModel(lat)
    z = {}
    for k, (_, p) in enumerate(reps):
        z[k] = lm.m.NewBoolVar(f"z{k}")
        for q in p:
            lm.m.Add(lm.x[q] == 1).OnlyEnforceIf(z[k])
    index = {r: k for k, r in enumerate(reps)}
    w = []
    for r1, r2 in stackable(reps):
        b = lm.m.NewBoolVar("")
        lm.m.AddImplication(b, z[index[r1]])
        lm.m.AddImplication(b, z[index[r2]])
        w.append(b)
    lm.m.Add(sum(w) >= 1)
    return lm


def by_cpsat(lat):
    # 1. two junctions
    lm = LogicalModel(lat)
    j = {}
    for v in lat.xy:
        if len(lat.nb[v]) == 3:
            j[v] = lm.m.NewBoolVar(f"j{v}")
            lm.m.Add(lm.x[v] == 0).OnlyEnforceIf(j[v])
            for t in lat.nb[v]:
                lm.m.Add(lm.x[t] == 1).OnlyEnforceIf(j[v])
    lm.m.Add(sum(j.values()) >= 2)
    two_junctions, status1, _ = lm.solve()
    # 2. two disjoint hook errors
    reps = hook_representatives(lat)
    two_hooks, status2, _ = stacking_model(lat, reps).solve()
    # control: single-color pairs on the red hexagons do stack
    control, status3, _ = stacking_model(lat, control_representatives(lat)).solve()
    return two_junctions, status1, two_hooks, status2, len(reps), control, status3


if __name__ == "__main__":
    ds = [int(a) for a in sys.argv[1:]] or [7, 9, 11]
    ok = True
    for d in ds:
        lat = Lattice(d)
        if d <= 9:
            ops = load_min_weight(d)[1]
            mj, stacked = by_enumeration(lat, ops)
            ctl_max = max(sum(1 for _, p in control_representatives(lat) if p <= L) for L in ops)
            print(f"d={d}, all {len(ops)} operators: at most {mj} junction(s) per operator; "
                  f"operators containing two disjoint hook errors: {stacked}; "
                  f"control: up to {ctl_max} red single-color pairs in one operator")
            ok &= mj == 1 and stacked == 0 and ctl_max >= 2
        tj, s1, th, s2, nrep, ctl, s3 = by_cpsat(lat)
        print(f"d={d}, CP-SAT: operator with two junctions: {s1}; "
              f"operator with two disjoint hook errors ({nrep} hook-error representatives): {s2}; "
              f"control, two disjoint red single-color pairs: {s3}")
        ok &= (not tj) and (not th) and ctl
    assert ok
    print("OK")
