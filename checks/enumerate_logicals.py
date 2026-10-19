"""Enumerate every minimum weight logical operator at d = 7 and d = 9.

Expected: the minimum weight is d, with 140 operators at d = 7 and 464 at d = 9. The enumeration is compared with
the cached copies in data/minlog_d7.json and data/minlog_d9.json (written if they are missing), and with
data/d9_lattice.json, the d = 9 lattice and operators used by the figure scripts."""
import json

import _setup  # noqa: F401
from jhe import Lattice
from jhe.logicals import DATA, enumerate_min_weight

EXPECTED = {7: 140, 9: 464}

ops9 = None
for d, n in EXPECTED.items():
    lat = Lattice(d)
    w, ops = enumerate_min_weight(lat)
    print(f"d={d}: {len(lat.xy)} data qubits, {len(lat.faces)} stabilizers; "
          f"minimum weight {w}, {len(ops)} minimum weight logical operators")
    assert w == d and len(ops) == n, "unexpected enumeration result"
    path = DATA / f"minlog_d{d}.json"
    if path.exists():
        cached = json.loads(path.read_text())
        assert cached["minw"] == w and {frozenset(o) for o in cached["ops"]} == set(ops), f"{path.name} differs"
        print(f"  matches {path.relative_to(DATA.parent)}")
    else:
        path.write_text(json.dumps({"minw": w, "ops": sorted(sorted(o) for o in ops)}))
        print(f"  wrote {path.relative_to(DATA.parent)}")
    if d == 9:
        ops9, lat9 = set(ops), lat

A = json.loads((DATA / "d9_lattice.json").read_text())
assert all(tuple(A["xy"][str(q)]) == lat9.xy[q] for q in lat9.xy) and len(A["xy"]) == len(lat9.xy)
assert {(f["c"], frozenset(f["qs"])) for f in A["faces"]} == {(f["c"], f["qs"]) for f in lat9.faces}
assert {frozenset(o) for o in A["ops"]} == ops9
print("data/d9_lattice.json has the authors' d=9 layout and the same 464 operators")
print("OK")
