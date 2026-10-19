#!/usr/bin/env bash
# Check out the code released with Kishony & Fowler, "Color code off-the-hook" (arXiv:2603.28852), at the commit
# used for the note. Only the syndrome_extraction_optimization directory of the Classiq library is checked out.
set -euo pipefail
COMMIT=3c609cd459ad1e164549ef84339f00718f37c546
DEST="$(cd "$(dirname "$0")" && pwd)/external/classiq-library"
if [ ! -d "$DEST/.git" ]; then
  git clone --filter=blob:none --no-checkout https://github.com/Classiq/classiq-library.git "$DEST"
fi
cd "$DEST"
git sparse-checkout set algorithms/error_correction/syndrome_extraction_optimization
git checkout --quiet "$COMMIT"
echo "Kishony-Fowler code at $DEST/algorithms/error_correction/syndrome_extraction_optimization (commit $COMMIT)"
