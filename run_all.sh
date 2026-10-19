#!/usr/bin/env bash
# Runs every check and regenerates every figure of the note. Each check stops with an error if a number differs
# from the note. Most of the running time is spent on d = 11 and on the d = 9 integer program.
set -euo pipefail
cd "$(dirname "$0")"
PY="${PYTHON:-python3}"
for s in enumerate_logicals hook_classification fault_injection weight4_stabilizers junctions_and_stacking bulk_only_distance; do
  echo "== checks/$s.py"
  "$PY" checks/$s.py
done
for f in fig_junction_hook_d9 fig_string_colors_d9 fig_kf_pairs_and_schedule_d9 fig_single_hook_shortcuts_d9; do
  echo "== figures/$f.py"
  "$PY" figures/$f.py
done
"$PY" figures/witnesses.py | tail -1
echo "Figures written to figures/output/"
