"""The weight-4 boundary stabilizers and the hexagons (Sec. 3.1 of the note, last paragraph).

1. d = 9, by enumeration: for every non-corner weight-4 stabilizer, the two diagonals (the two representatives of its
   hook error) lie on the same number of minimum weight logical operators. One diagonal is a junction pair in every
   one of them. The other is never a junction pair, is perpendicular to the boundary of the stabilizer's color, and
   meets the criterion of Kishony and Fowler for a single-color malign pair: at each end, the edge leaving the
   stabilizer has the stabilizer's color and is nearly perpendicular (30 degrees from perpendicular) to the boundary
   of that color.
2. d = 7, 9 and 11, by CP-SAT: each of the three ways of pairing the four data qubits of a non-corner weight-4
   stabilizer lies on a minimum weight logical operator (either pair of the pairing may be the one contained), so
   every possible weight-2 hook error on these stabilizers reduces the distance, whatever the CNOT order.
3. d = 9, by enumeration: whenever a weight-2 hook error of a non-corner hexagon lies on a minimum weight logical
   operator, it is a junction pair of that operator."""
import sys
from collections import Counter

import _setup  # noqa: F401
from jhe import Lattice
from jhe.logicals import exists, load_min_weight


def diagonals_d9():
    lat = Lattice(9)
    ops = load_min_weight(9)[1]
    ok = True
    for f in lat.non_corner_faces():
        if f["kind"] != "trap":
            continue
        (h,) = lat.hook_errors(f)
        info = []
        for a, b in h["pairs"]:
            Ls = [L for L in ops if a in L and b in L]
            junction = sum(lat.is_junction_pair(a, b, L) for L in Ls)
            outgoing = [(q, t) for q in (a, b) for t in lat.nb[q] - f["qs"]]
            criterion = bool(outgoing) and all(lat.edge_color(q, t) == f["c"] and
                                               abs(lat.off_perpendicular(q, t, f["c"]) - 30) < 1e-6
                                               for q, t in outgoing)
            info.append({"pair": (a, b), "n": len(Ls), "junction": junction,
                         "off_perp": round(lat.off_perpendicular(a, b, f["c"])), "criterion": criterion})
        j = [i for i in info if i["junction"] == i["n"] > 0]
        o = [i for i in info if i["junction"] == 0]
        good = (len(j) == 1 and len(o) == 1 and info[0]["n"] == info[1]["n"] > 0
                and o[0]["off_perp"] == 0 and o[0]["criterion"])
        ok &= good
        print(f"  {f['c']} stabilizer {sorted(f['qs'])}: junction diagonal {j[0]['pair'] if j else None}, "
              f"other diagonal {o[0]['pair'] if o else None} ({o[0]['off_perp'] if o else '?'} deg from "
              f"perpendicular, criterion met: {o[0]['criterion'] if o else '?'}); "
              f"{info[0]['n']} logical operators each -> {'ok' if good else 'FAILED'}")
    return ok


def pairings(d):
    lat = Lattice(d)
    tally = Counter()
    for f in lat.non_corner_faces():
        if f["kind"] != "trap":
            continue
        a, b, c, e = sorted(f["qs"])
        result = []
        for p, q in (((a, b), (c, e)), ((a, c), (b, e)), ((a, e), (b, c))):
            result.append(exists(lat, contains=p)[0] or exists(lat, contains=q)[0])
        tally[tuple(result)] += 1
    print(f"  d={d}: {sum(tally.values())} non-corner weight-4 stabilizers; "
          f"all three pairings on a minimum weight logical operator for {tally[(True, True, True)]} of them")
    return set(tally) == {(True, True, True)}


def hexagons_d9():
    lat = Lattice(9)
    ops = load_min_weight(9)[1]
    tally = Counter()
    for f in lat.non_corner_faces():
        if f["kind"] != "hex":
            continue
        for h in lat.hook_errors(f):
            (a, b), = h["pairs"]
            for L in ops:
                if a in L and b in L:
                    tally[lat.is_junction_pair(a, b, L)] += 1
    print(f"  d=9: hexagon hook errors on a minimum weight logical operator: {tally[True]} times as a junction pair, "
          f"{tally[False]} times otherwise")
    return tally[False] == 0 and tally[True] > 0


if __name__ == "__main__":
    print("1. Diagonals of the weight-4 stabilizers, d=9")
    r1 = diagonals_d9()
    print("2. All pairings of the weight-4 stabilizers")
    ds = [int(a) for a in sys.argv[1:]] or [7, 9, 11]
    r2 = all(pairings(d) for d in ds)
    print("3. Hexagons")
    r3 = hexagons_d9()
    assert r1 and r2 and r3
    print("OK")
