"""Classify the weight-2 hook errors of the schedule on every non-corner stabilizer (Sec. 3.1 of the note).

A hook error is
  benign    if no minimum weight logical operator contains it,
  junction  if some minimum weight logical operator L contains it as a junction pair, i.e. as the two neighbors,
            on one stabilizer, of a data qubit outside L whose three neighbors are all in L,
  other     if it is contained in a minimum weight logical operator but never as a junction pair.
The hook error of a weight-4 stabilizer has two representatives (equal up to the stabilizer); it is contained in L
if either representative is.

Expected at d = 7, 9 and 11 (15, 27 and 42 non-corner stabilizers): on every weight-6 stabilizer exactly one of the
two hook errors is a junction hook error and the other is benign; the hook error of every weight-4 stabilizer is a
junction hook error. On the bulk stabilizers the junction hook error is the pair of the note: bottom-right and left
(time steps 5, 6) on red, top-right and left (1, 2) on green, top-right and bottom-right (5, 6) on blue.

d = 7 and 9 use the enumerated operators; d = 11 uses CP-SAT, where every 'benign' answer is a proof of
infeasibility (an undecided instance raises an error instead)."""
import sys
from collections import Counter

import _setup  # noqa: F401
from jhe import Lattice
from jhe.logicals import exists, load_min_weight

BULK_JUNCTION = {"r": ("BR", "L"), "g": ("TR", "L"), "b": ("TR", "BR")}
EXPECTED_COUNTS = {7: 15, 9: 27, 11: 42}


def classify_by_enumeration(lat, ops):
    def label(h):
        hits = [(L, a, b) for a, b in h["pairs"] for L in ops if a in L and b in L]
        if not hits:
            return "benign"
        return "junction" if any(lat.is_junction_pair(a, b, L) for L, a, b in hits) else "other"
    return label


def classify_by_cpsat(lat):
    def label(h):
        for a, b in h["pairs"]:
            for v in lat.nb[a] & lat.nb[b]:
                if len(lat.nb[v]) == 3 and exists(lat, contains=lat.nb[v], excludes=[v])[0]:
                    return "junction"
        malign = any(exists(lat, contains=(a, b))[0] for a, b in h["pairs"])
        return "other" if malign else "benign"
    return label


def run(d):
    lat = Lattice(d)
    label = classify_by_enumeration(lat, load_min_weight(d)[1]) if d <= 9 else classify_by_cpsat(lat)
    faces = lat.non_corner_faces()
    tally = Counter()
    bulk_ok = True
    for f in faces:
        hooks = lat.hook_errors(f)
        labels = [label(h) for h in hooks]
        where = "bulk" if f["interior"] else "boundary"
        tally[(f["kind"], where, tuple(sorted(labels)))] += 1
        if f["interior"]:
            names = {n for n, q in f["lab"].items() if q in hooks[labels.index("junction")]["pairs"][0]}
            bulk_ok &= names == set(BULK_JUNCTION[f["c"]])
    print(f"d={d}: {len(faces)} non-corner stabilizers")
    for (kind, where, labels), n in sorted(tally.items()):
        print(f"  {n:2d} {where:8s} weight-{6 if kind == 'hex' else 4} stabilizers: hook errors {', '.join(labels)}")
    ok = len(faces) == EXPECTED_COUNTS[d] and bulk_ok and all(
        labels == (("benign", "junction") if kind == "hex" else ("junction",)) for kind, _, labels in tally)
    print(f"  bulk junction hook errors at the corners stated in the note: {bulk_ok}")
    return ok


if __name__ == "__main__":
    ds = [int(a) for a in sys.argv[1:]] or [7, 9, 11]
    results = {d: run(d) for d in ds}
    assert all(results.values()), results
    print("OK")
