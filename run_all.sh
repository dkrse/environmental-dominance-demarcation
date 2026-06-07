#!/usr/bin/env bash
# Run the full analysis pipeline: recompute every result, table value and figure
# from data/ into output/.
#
# Usage:
#   ./run_all.sh
#
# See INSTALL.md for prerequisites and what each step produces.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

PY="${PYTHON:-python3}"

echo "==> Using interpreter: $($PY --version 2>&1)"

# Integrity gate: refuse to run if any input in data/ differs from the recorded
# SHA-256 manifest, so a changed input can never silently alter the results.
echo "==> [check_data]"
$PY scripts/check_data.py

# Analysis pipeline (each script reads data/, writes output/). Order matters:
# make_figures.py consumes the JSON/CSV produced by the steps above it.
STEPS=(
  probe_a_sentinel        # Probe A: sentinel leverage on the variance decomposition
  probe_a_imputation      # Probe A: imputation counterweight (within-component band)
  probe_b_within_us       # Probe B: within-US transmission-law slope test
  probe_b_power           # Probe B: power analysis (MDE, power at slope=1)
  probe_b_cross_country   # Probe B: cross-country slope (contaminated vs clean)
  probe_c_interlock       # Probe C: visible board-interlock concentration
  probe_d_place_decoupling # Probe D: causal place effect at fixed parental rank
  opacity_concentration   # Opacity: hidden-layer degree concentration
  opacity_by_jurisdiction # Opacity: UBO rate by jurisdiction + by source
  opacity_disentangle     # Opacity: eta^2 source vs jurisdiction
  hierarchical_icc        # ICC decomposition (between vs within country)
  csn_powerlaw            # Clauset-Shalizi-Newman power-law tests (slow: ~minutes)
  make_figures            # fig1-3 PNGs (run last)
)

for s in "${STEPS[@]}"; do
  echo "==> [$s]"
  $PY "scripts/$s.py"
done

echo "==> Done. Artifacts in output/ (JSON/CSV) and output/figures/ (PNG)."
