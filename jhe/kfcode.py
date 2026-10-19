"""Access to the code released with Kishony and Fowler, "Color code off-the-hook: avoiding hook errors with a
single auxiliary per plaquette" (arXiv:2603.28852).

Their code is part of the Classiq library (MIT license),
https://github.com/Classiq/classiq-library/tree/main/algorithms/error_correction/syndrome_extraction_optimization
Run ./fetch_kf_code.sh once to check out the commit used for the note into external/, or set the KF_CODE
environment variable to an existing copy of the syndrome_extraction_optimization directory.

Only three things are taken from their code: the color-code layout (their ColorCode class), the CNOT schedule
(row 0 of results/zero_collision_schedules.csv) and the circuit builder build_parallel_circuit, plus their integer
program for the exact circuit-level distance (ilp_circuit_distance.py). The two functions are read out of
benchmark_circuits.py with the ast module, so that the decoder and plotting dependencies imported at the top of that
file are not needed."""
import ast
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KF_COMMIT = "3c609cd459ad1e164549ef84339f00718f37c546"
_DEFAULT = ROOT / "external" / "classiq-library" / "algorithms" / "error_correction" / "syndrome_extraction_optimization"

# The schedule used throughout the note: CNOT time step for the data qubits at the authors' offsets
# (top-left, top-right, right, bottom-right, bottom-left, left).
EXPECTED_SCHEDULE = {"r": [1, 3, 2, 5, 4, 6], "g": [5, 1, 4, 3, 6, 2], "b": [1, 5, 3, 6, 2, 4]}

_ns = None


def kf_dir() -> Path:
    p = Path(os.environ.get("KF_CODE", _DEFAULT))
    if not (p / "benchmark_circuits.py").exists():
        sys.exit(f"The Kishony-Fowler code was not found at {p}.\n"
                 "Run ./fetch_kf_code.sh from the repository root, or set KF_CODE to the "
                 "syndrome_extraction_optimization directory of the Classiq library.")
    return p


def _placeholder_cairosvg():
    """The authors' color_code_stim_local package imports cairosvg, which it uses only to render drawings. Nothing
    here draws with it, so if cairosvg (or the cairo library it needs) is missing, a placeholder module is used."""
    try:
        import cairosvg  # noqa: F401
    except (ImportError, OSError):
        import types
        m = types.ModuleType("cairosvg")

        def svg2png(*args, **kwargs):
            raise RuntimeError("cairosvg is not installed")
        m.svg2png = svg2png
        sys.modules["cairosvg"] = m


def _load():
    global _ns
    if _ns is None:
        d = kf_dir()
        if str(d) not in sys.path:
            sys.path.insert(0, str(d))
        _placeholder_cairosvg()
        ns = {}
        exec("import stim\nfrom typing import Dict\nfrom color_code_stim_local import ColorCode\n", ns)
        tree = ast.parse((d / "benchmark_circuits.py").read_text())
        wanted = ("build_parallel_circuit", "load_zero_collision_schedule")
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name in wanted:
                exec(compile(ast.Module([node], []), "benchmark_circuits.py", "exec"), ns)
        missing = [w for w in wanted if w not in ns]
        if missing:
            sys.exit(f"Could not find {missing} in {d / 'benchmark_circuits.py'}")
        _ns = ns
    return _ns


def color_code(d: int):
    """The authors' ColorCode object, used only for its qubit layout."""
    return _load()["ColorCode"](d=d, rounds=1, cnot_schedule="tri_optimal", p_cnot=0,
                                exclude_non_essential_pauli_detectors=True,
                                _generate_dem=False, _decompose_dem=False)


def schedule_config() -> dict:
    """Row 0 of the authors' zero-collision schedules, the schedule of their Fig. 1(b)."""
    cfg = _load()["load_zero_collision_schedule"](str(kf_dir() / "results" / "zero_collision_schedules.csv"), 0)
    got = {c: list(cfg[c + "_schedule"]) for c in "rgb"}
    assert got == EXPECTED_SCHEDULE, f"unexpected schedule in the authors' CSV: {got}"
    return cfg


def noiseless_circuit(d: int, rounds: int):
    """The authors' memory circuit (Z-type stabilizers at CNOT steps 1-6, X-type at 7-12), without noise."""
    return _load()["build_parallel_circuit"](d, rounds, 0.0, schedule_config())


def mip_circuit_distance(dem, **kwargs):
    """The authors' integer program for the exact circuit-level distance of a detector error model."""
    kf_dir()
    _load()
    from ilp_circuit_distance import mip_circuit_distance as f
    return f(dem, **kwargs)
