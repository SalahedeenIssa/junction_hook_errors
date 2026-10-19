"""The triangular 6.6.6 color code in the layout of the authors' code, with the Kishony-Fowler schedule.

Coordinates are the authors' (x in half-edge units, y = row of the lattice). Data qubit q is the q-th entry of
ColorCode.qubit_groups['data']; every stabilizer is given by its ancilla position and the data qubits at the six
offsets used by the authors (top-left, top-right, right, bottom-right, bottom-left, left). In this layout the red
boundary is at the bottom, the green boundary on the left and the blue boundary on the right."""
import math
from collections import Counter

from .kfcode import color_code, schedule_config

NAMES = ("TL", "TR", "R", "BR", "BL", "L")
OFFSETS = ((-2, 1), (2, 1), (4, 0), (2, -1), (-2, -1), (-4, 0))
ROW = 2 * math.sqrt(3)                     # height of one row when the edge length is 4
# inward normals of the three boundaries, in degrees
BOUNDARY_NORMAL = {"r": 90.0, "g": -30.0, "b": 210.0}


class Lattice:
    def __init__(self, d: int):
        cc = color_code(d)
        data = cc.qubit_groups["data"]
        self.d = d
        self.xy = {i: (v["x"], v["y"]) for i, v in enumerate(data)}
        index = {xy: i for i, xy in self.xy.items()}
        cfg = schedule_config()
        self.sched = {c: dict(zip(NAMES, cfg[c + "_schedule"])) for c in "rgb"}
        self.nb = {q: {p for p in self.xy if p != q and abs(math.dist(self.pos(p), self.pos(q)) - 4) < 1e-9}
                   for q in self.xy}
        self.faces = []
        for a in cc.qubit_groups["anc_Z"]:
            lab = {}
            for n, (dx, dy) in zip(NAMES, OFFSETS):
                q = index.get((a["x"] + dx, a["y"] + dy))
                if q is not None:
                    lab[n] = q
            order = sorted(lab, key=lambda n: self.sched[a["color"]][n])
            self.faces.append({"c": a["color"], "lab": lab, "qs": frozenset(lab.values()),
                               "anc": (a["x"], a["y"]), "kind": "hex" if len(lab) == 6 else "trap",
                               "order": order, "boundary": a["boundary"]})
        nface = Counter(q for f in self.faces for q in f["qs"])
        self.corner_qubits = {q for q in self.xy if nface[q] == 1}
        for f in self.faces:
            f["corner"] = bool(f["qs"] & self.corner_qubits)
            f["interior"] = all(len(self.nb[q]) == 3 for q in f["qs"])

    # geometry -----------------------------------------------------------------------------------------------
    def pos(self, q):
        x, y = self.xy[q]
        return (x, y * ROW)

    def angle(self, a, b):
        (x1, y1), (x2, y2) = self.pos(a), self.pos(b)
        return math.degrees(math.atan2(y2 - y1, x2 - x1))

    def off_perpendicular(self, a, b, c):
        """Angle (degrees, 0-90) between the segment a-b and the normal of the boundary of color c."""
        t = abs(self.angle(a, b) % 180 - BOUNDARY_NORMAL[c] % 180) % 180
        return min(t, 180 - t)

    def edge_color(self, a, b):
        """Color of the edge a-b: X errors on both ends flip only stabilizers of this color."""
        flipped = {f["c"] for f in self.faces if len(f["qs"] & {a, b}) == 1}
        assert len(flipped) == 1, (a, b, flipped)
        return flipped.pop()

    def non_corner_faces(self):
        return [f for f in self.faces if not f["corner"]]

    # hook errors --------------------------------------------------------------------------------------------
    def hook_errors(self, f):
        """The weight-2 hook errors of stabilizer f under the schedule.

        Each is a dict with 'pairs', the pairs of data qubits it is equivalent to (up to the stabilizer),
        'after', the CNOT time step (1-6) after which the ancilla fault occurs, and 'label'. On a weight-6
        stabilizer a fault after the 4th CNOT acts on positions (5,6) and a fault after the 2nd CNOT acts on
        positions (3,4,5,6), i.e. on (1,2) up to the stabilizer. On a weight-4 stabilizer a fault after the 2nd
        CNOT acts on the last two data qubits, i.e. on the first two up to the stabilizer."""
        o, lab, t = f["order"], f["lab"], self.sched[f["c"]]
        if f["kind"] == "hex":
            return [{"pairs": [(lab[o[0]], lab[o[1]])], "after": t[o[1]], "label": "positions 1,2"},
                    {"pairs": [(lab[o[4]], lab[o[5]])], "after": t[o[3]], "label": "positions 5,6"}]
        return [{"pairs": [(lab[o[2]], lab[o[3]]), (lab[o[0]], lab[o[1]])], "after": t[o[1]],
                 "label": "last two (= first two)"}]

    # junctions ----------------------------------------------------------------------------------------------
    def junctions(self, L):
        """Data qubits v not in L whose three neighbors all belong to L."""
        return [v for v in self.xy if v not in L and len(self.nb[v]) == 3 and self.nb[v] <= L]

    def is_junction_pair(self, a, b, L):
        """True if a and b are the two neighbors of a junction of L on a stabilizer that contains it."""
        return any(v not in L and len(self.nb[v]) == 3 and self.nb[v] <= L for v in self.nb[a] & self.nb[b])
