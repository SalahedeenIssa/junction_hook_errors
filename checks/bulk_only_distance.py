"""Exact circuit-level distance with noise only in the bulk (Sec. 3.2 of the note).

All noise is removed from the authors' circuit except
  - two-qubit depolarizing noise after every CNOT of a bulk stabilizer (a stabilizer none of whose data qubits lies
    on the boundary), and
  - single-qubit depolarizing noise on every data qubit once per round, before the round's first CNOT layer.
The exact circuit-level distance is then computed with the integer program released with the authors' code.
Expected: 6 at d = 7 and 8 at d = 9, one less than the code distance. As a control, with the noise on the bulk
CNOTs also removed the distance is d.

The number of rounds can be changed with --rounds (default 2). At d = 7 the result is the same with 3 and 7 rounds.
The d = 9 integer program takes about ten minutes; run `python checks/bulk_only_distance.py 7` for a quick check."""
import argparse
import time

import stim

import _setup  # noqa: F401
from jhe import Lattice
from jhe.kfcode import mip_circuit_distance, noiseless_circuit

EXPECTED = {7: 6, 9: 8}


def bulk_noise_circuit(d, rounds, p=1e-3, cnot_noise=True):
    lat = Lattice(d)
    c = noiseless_circuit(d, rounds)
    coords = {int(i.targets_copy()[0].value): tuple(i.gate_args_copy()) for i in c if i.name == "QUBIT_COORDS"}
    by_xy = {(x, y): q for q, (x, y) in coords.items()}
    qid = lambda xy: by_xy[(float(xy[0]), float(xy[1]))]
    data = sorted(qid(xy) for xy in lat.xy.values())
    bulk = {qid(f["anc"]) for f in lat.faces if f["interior"]}
    out = stim.Circuit()
    layer = 0
    for inst in c:
        if inst.name == "CX":
            if layer % 12 == 0:                       # first CNOT layer of a round
                out.append("DEPOLARIZE1", data, p)
            layer += 1
            out.append(inst)
            if cnot_noise:
                t = inst.targets_copy()
                for a, b in zip(t[::2], t[1::2]):
                    if a.value in bulk or b.value in bulk:
                        out.append("DEPOLARIZE2", [a.value, b.value], p)
        else:
            out.append(inst)
    return out, len(bulk)


def distance(circuit):
    dem = circuit.detector_error_model(decompose_errors=False)
    r = mip_circuit_distance(dem)
    assert r["status"] == "OPTIMAL", r["status"]
    return r["distance"], dem.num_errors


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("d", type=int, nargs="*", default=[7, 9])
    ap.add_argument("--rounds", type=int, default=2)
    args = ap.parse_args()
    ok = True
    for d in args.d:
        for cnot_noise in (True, False):
            t0 = time.time()
            c, nbulk = bulk_noise_circuit(d, args.rounds, cnot_noise=cnot_noise)
            dist, nerr = distance(c)
            want = EXPECTED.get(d, d - 1) if cnot_noise else d
            what = (f"noise on the CNOTs of the {nbulk} bulk stabilizers and on the data qubits" if cnot_noise
                    else "noise on the data qubits only")
            print(f"d={d}, {args.rounds} rounds, {what}: circuit-level distance {dist} "
                  f"(expected {want}; {nerr} error mechanisms, {time.time() - t0:.0f} s)", flush=True)
            ok &= dist == want
    assert ok
    print("OK")
