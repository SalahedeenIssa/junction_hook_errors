"""Fault injection into the authors' circuit with Stim (Sec. 3.1, Fig. 1 and Fig. 4 of the note).

1. For every non-corner stabilizer at d = 7, 9 and 11, a minimum weight logical operator L is found (CP-SAT) in which
   the stabilizer's junction hook error is a junction pair. The hook fault (an X error on the ancilla right after the
   relevant CNOT) is injected together with X errors on the other d - 2 data qubits of L.
2. The three junction hook errors of Fig. 1, at positions 5,6 of the red stabilizer, 1,2 of the green stabilizer and
   5,6 of the blue stabilizer, each with the other seven data qubits of the logical operator drawn there.
3. The nine examples of Fig. 4 (data/witnesses.json).
Expected in every case: no detector fires and the logical observable flips, i.e. an undetectable logical error made
of d - 1 faults."""
import json
import sys

import _setup  # noqa: F401
from jhe import Lattice
from jhe.faults import Circuit
from jhe.logicals import DATA, exists

FIG1_L = [3, 11, 27, 34, 35, 36, 39, 42, 43]
FIG1_PAIRS = {"r": ((34, 39), "positions 5,6"), "g": ((27, 34), "positions 1,2"), "b": ((27, 39), "positions 5,6")}


def hook_of(lat, pair):
    """The stabilizer and hook error of the schedule that have `pair` as a representative."""
    for f in lat.faces:
        for h in lat.hook_errors(f):
            if any(set(p) == set(pair) for p in h["pairs"]):
                return f, h
    raise ValueError(f"{pair} is not a weight-2 hook error of the schedule")


def undetectable_logical(circ, lat, f, h, pair, L):
    data = [lat.xy[q] for q in L if q not in pair]
    return circ.inject(f["anc"], h["after"], data) == (False, True)


def sweep(d):
    lat, circ = Lattice(d), Circuit(d)
    passed = 0
    faces = lat.non_corner_faces()
    for f in faces:
        found = None
        for h in lat.hook_errors(f):
            for a, b in h["pairs"]:
                for v in lat.nb[a] & lat.nb[b]:
                    if len(lat.nb[v]) == 3:
                        ok, L = exists(lat, contains=lat.nb[v], excludes=[v])
                        if ok:
                            found = (h, (a, b), L)
                            break
                if found: break
            if found: break
        assert found, f"no junction hook error found on {sorted(f['qs'])}"
        h, pair, L = found
        passed += undetectable_logical(circ, lat, f, h, pair, L)
    print(f"d={d}: undetectable logical error with d-1 = {d - 1} faults on {passed} of {len(faces)} "
          "non-corner stabilizers")
    return passed == len(faces)


def figure_examples():
    lat, circ = Lattice(9), Circuit(9)
    L = set(FIG1_L)
    ok = True
    for c, (pair, label) in FIG1_PAIRS.items():
        f, h = hook_of(lat, pair)
        good = f["c"] == c and h["label"] == label and lat.is_junction_pair(*pair, L)
        good &= undetectable_logical(circ, lat, f, h, pair, L)
        print(f"Fig. 1, {f['c']} stabilizer, {h['label']}: pair {pair} -> {'ok' if good else 'FAILED'}")
        ok &= good
    W = json.loads((DATA / "witnesses.json").read_text())
    for k, w in sorted(W.items()):
        pair, L = tuple(w["pair"]), set(w["L"])
        f, h = hook_of(lat, pair)
        good = set(w["face"]) == f["qs"] and len(L) == 9 and lat.is_junction_pair(*pair, L)
        good &= undetectable_logical(circ, lat, f, h, pair, L)
        print(f"Fig. 4({k}) {w['title']}: pair {pair} -> {'ok' if good else 'FAILED'}")
        ok &= good
    return ok


if __name__ == "__main__":
    ds = [int(a) for a in sys.argv[1:]] or [7, 9, 11]
    results = [sweep(d) for d in ds]
    results.append(figure_examples())
    assert all(results)
    print("OK")
