# Junction hook errors in the color code

Code for the note *Junction Hook Errors in the Color Code* by Salahedeen Issa and Margaret Martonosi
(Princeton University).

The note examines the syndrome extraction schedule for the triangular color code proposed by Kishony and Fowler in
[*Color code off-the-hook: avoiding hook errors with a single auxiliary per plaquette*](https://arxiv.org/abs/2603.28852)
(arXiv:2603.28852). Under that schedule, every non-corner stabilizer has a weight-2 hook error that, together with
d − 2 data qubit errors, produces an undetectable logical error. Each of these is a *junction hook error*: its two
data qubits are the two neighbors, on one stabilizer, of the point where the strings of a minimum weight logical
operator meet.

This repository contains the code behind every check and figure in the note. Each script in `checks/` tests one
group of statements and stops with an error if a result differs from the note.

## Setup

Tested with Python 3.11 on Linux. A C compiler (`cc`) is needed to enumerate logical operators.

```bash
pip install -r requirements.txt
./fetch_kf_code.sh
```

`fetch_kf_code.sh` checks out the code released with Kishony and Fowler, part of the
[Classiq library](https://github.com/Classiq/classiq-library/tree/main/algorithms/error_correction/syndrome_extraction_optimization)
(MIT license), into `external/`, at the commit used for the note (`3c609cd`). Only its
`syndrome_extraction_optimization` directory is checked out. If you already have a copy of that directory, set the
`KF_CODE` environment variable to it instead.

Four things are taken from their code: the color code layout (their `ColorCode` class), the CNOT schedule (row 0 of
`results/zero_collision_schedules.csv`), their circuit builder `build_parallel_circuit`, and their integer program
for the exact circuit-level distance (`ilp_circuit_distance.py`). None of their code is copied into this repository.
Their `ColorCode` package also imports `cairosvg` for drawing; nothing here needs it, so a placeholder module is used
when it is not installed.

## Checks

| Script | What it checks | In the note |
|---|---|---|
| `checks/enumerate_logicals.py` | Every minimum weight logical operator: 140 at d = 7 and 464 at d = 9. | Sec. 3.1 |
| `checks/hook_classification.py` | On every non-corner stabilizer at d = 7, 9 and 11, one of the two hook errors of a weight-6 stabilizer is a junction hook error and the other lies on no minimum weight logical operator, and the hook error of a weight-4 stabilizer is a junction hook error. On the bulk stabilizers it is the pair coupled at time steps 5, 6 (red), 1, 2 (green) and 5, 6 (blue). | Abstract, Sec. 3.1 |
| `checks/fault_injection.py` | In the authors' circuit, each of these hook errors together with d − 2 data qubit errors fires no detector and flips the logical observable (d = 7, 9 and 11). The same holds for the hook errors drawn in Figures 1 and 4. | Sec. 3.1, Figs. 1 and 4 |
| `checks/weight4_stabilizers.py` | On each weight-4 stabilizer, the diagonal that is not a junction pair is perpendicular to the boundary of the stabilizer's color and meets Kishony and Fowler's single-color criterion. Every pairing of the four data qubits lies on a minimum weight logical operator (d = 7, 9 and 11). A hexagon's hook error lies on a minimum weight logical operator only at its junction (d = 9). | Sec. 3.1 |
| `checks/junctions_and_stacking.py` | No minimum weight logical operator has two junctions or contains two disjoint hook errors of the schedule, corner stabilizers included (d = 7, 9 and 11). A control shows that single-color malign pairs, by contrast, do accumulate. | Abstract, Sec. 1, Sec. 4 |
| `checks/bulk_only_distance.py` | The exact circuit-level distance with noise only on the CNOTs of the bulk stabilizers and on the data qubits: 6 at d = 7 and 8 at d = 9. Without the CNOT noise it is d. | Sec. 3.2 |

Run a check with `python checks/<name>.py`. The checks take the distances as arguments, for example
`python checks/hook_classification.py 7 9` leaves out d = 11. The slow parts are the d = 11 searches and the d = 9
integer program; with d = 7 and 9 only (d = 7 only for `bulk_only_distance.py`), every check finishes within a few
minutes. `./run_all.sh` runs every check and figure script.

At d = 7 and 9 the checks go through every enumerated minimum weight logical operator. At d = 11 there are too many
to enumerate (the logical coset has 2^45 elements), so each question is posed to the CP-SAT solver of OR-Tools as
"is there a weight-11 logical operator with these properties?". A "no" from the solver is a proof of infeasibility;
an instance the solver does not decide is reported as an error, never counted as a "no".

## Figures

| Figure in the note | Script | Output |
|---|---|---|
| Figure 1 | `figures/fig_junction_hook_d9.py` | `fig_junction_hook_d9.pdf` |
| Figure 2 | `figures/fig_string_colors_d9.py` | `fig_string_colors_d9.pdf` |
| Figure 3 | `figures/fig_kf_pairs_and_schedule_d9.py` | `fig_kf_pairs_and_schedule_d9.pdf` |
| Figure 4 | `figures/fig_single_hook_shortcuts_d9.py` | `fig_single_hook_shortcuts_d9.pdf` |

The figures are written to `figures/output/` and need only NumPy and Matplotlib. Helpers:

- `figures/fig_kf_malign_pairs_junction_d9.py` draws panel (a) of Figure 3. Its red, green and blue pairs are
  transcribed from Fig. 1(a) of Kishony and Fowler, and the script checks that each lies on a minimum weight logical
  operator.
- `figures/strings_examples.py` describes the two logical operators of Figure 2 link by link.
- `figures/witnesses.py` chooses the nine examples of Figure 4 and compares them with `data/witnesses.json`.

## Conventions

- The layout and qubit indices are those of the authors' code: data qubit q is entry q of
  `ColorCode.qubit_groups['data']`. The red boundary is at the bottom, the green boundary on the left and the blue
  boundary on the right.
- The data qubits of a stabilizer are named by their position around its center: top-left (TL), top-right (TR),
  right (R), bottom-right (BR), bottom-left (BL) and left (L). In that order, the schedule couples them at time steps
  red [1, 3, 2, 5, 4, 6], green [5, 1, 4, 3, 6, 2] and blue [1, 5, 3, 6, 2, 4]. The weight-4 boundary stabilizers
  use the same order, without their two missing data qubits.
- Only X-type errors are considered, since the code is self-dual. In each round, the authors' circuit measures the
  Z-type stabilizers with CNOT steps 1–6 and the X-type stabilizers with steps 7–12 on the same ancillas. An X error
  on an ancilla after an X-type CNOT spreads to the data qubits coupled after it.
- The weight-2 hook errors of a weight-6 stabilizer act on the data qubits at positions (5, 6) of the schedule (a
  fault after the fourth CNOT) and, up to the stabilizer, on positions (1, 2) (a fault after the second CNOT). The
  weight-2 hook error of a weight-4 stabilizer acts on its last two data qubits, or equivalently its first two.
- A junction of a minimum weight logical operator L is a data qubit outside L whose three neighbors are all in L.
  A junction pair is two of those neighbors that lie on one stabilizer.

## Repository layout

```
jhe/                 shared code
  kfcode.py          loads the authors' layout, schedule, circuit builder and integer program
  lattice.py         lattice, schedule, hook errors and junctions for any distance
  logicals.py        enumeration of minimum weight logical operators, and CP-SAT models
  faults.py          fault injection into the authors' circuit with Stim
enum/enum.c          exhaustive search over the logical coset, used for d = 7 and 9
checks/              one script per group of statements in the note
figures/             the four figures and their helpers
data/
  minlog_d7.json     every minimum weight logical operator at d = 7 (lists of data qubit indices)
  minlog_d9.json     the same at d = 9
  d9_lattice.json    the d = 9 layout and its 464 operators, in the form used by the figure scripts
  witnesses.json     the examples of Figure 4
fetch_kf_code.sh     checks out the authors' code into external/
run_all.sh           runs every check and figure script
```

## License

MIT (see `LICENSE`). The authors' code is not part of this repository and keeps its own license.
