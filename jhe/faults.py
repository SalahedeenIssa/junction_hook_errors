"""Fault injection into the authors' circuit with Stim.

In each round of the authors' circuit the Z-type stabilizers are measured with CNOT steps 1-6 and the X-type
stabilizers, on the same ancillas, with steps 7-12 (ancilla as control). An X error on an ancilla right after the
X-type CNOT at schedule step t (circuit step 6 + t) therefore spreads to the data qubits coupled after it: this is
the hook error. The function `inject` adds such a fault, together with X errors on chosen data qubits, to a noiseless
circuit and reports whether any detector fires and whether the logical observable flips."""
import stim

from .kfcode import noiseless_circuit


class Circuit:
    def __init__(self, d, rounds=3):
        self.d = d
        self.rounds = rounds
        self.circuit = noiseless_circuit(d, rounds)
        coords = {int(i.targets_copy()[0].value): tuple(i.gate_args_copy())
                  for i in self.circuit if i.name == "QUBIT_COORDS"}
        self._by_xy = {(float(x), float(y)): q for q, (x, y) in coords.items()}

    def qubit(self, xy):
        """Circuit qubit index of the data qubit or ancilla at the authors' coordinates xy."""
        return self._by_xy[(float(xy[0]), float(xy[1]))]

    def inject(self, ancilla_xy, schedule_step, data_xy, round_index=1):
        """X on the ancilla at `ancilla_xy` right after X-type CNOT step `schedule_step` (1-6) of round
        `round_index`, plus X on the data qubits at the coordinates in `data_xy` at the same moment.
        Returns (any detector fired, logical observable flipped)."""
        anc = self.qubit(ancilla_xy)
        data = sorted(self.qubit(p) for p in data_xy)
        after = 6 + schedule_step
        out = stim.Circuit()
        r, layer, done = -1, 0, False
        for inst in self.circuit:
            out.append(inst)
            if inst.name == "CX":
                if layer % 12 == 0:
                    r += 1
                layer += 1
                if not done and r == round_index and (layer - 1) % 12 + 1 == after:
                    out.append("X_ERROR", [anc], 1.0)
                    if data:
                        out.append("X_ERROR", data, 1.0)
                    done = True
        assert done, "fault location not found"
        det, obs = out.compile_detector_sampler().sample(1, separate_observables=True)
        return bool(det.any()), bool(obs.any())
