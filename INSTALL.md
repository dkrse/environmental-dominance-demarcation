# Installation & Reproduction

This repository recomputes every result, table value and figure from the raw
data in `data/`. The whole pipeline runs in a few minutes on a laptop.

## 1. Prerequisites

- **Python** ≥ 3.10 (developed on 3.12).
- The input data already shipped in `data/` (see [Data](#5-data) below). No
  network access or proprietary sources are needed.

## 2. Install Python dependencies

All packages are pinned in `requirements.txt`:

```
pandas      # data frames, group-by decompositions
numpy       # numerics
scipy       # linregress, t/noncentral-t, Spearman (Probe B + power analysis)
matplotlib  # figures 1-3
openpyxl    # read data/cz_mobility.xlsx (Probe B)
powerlaw    # Clauset-Shalizi-Newman power-law fits (csn_powerlaw.py)
```

Recommended — an isolated virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If you install into a system/PEP-668-managed Python instead of a venv, add
`--break-system-packages` to the `pip install`.

`powerlaw` (used by `csn_powerlaw.py`) pulls in `mpmath` and `tqdm` and is
occasionally missing from an otherwise-populated environment; if `./run_all.sh`
stops at the `csn_powerlaw` step with `ModuleNotFoundError: No module named
'powerlaw'`, install it on its own:

```bash
pip install powerlaw     # add --break-system-packages outside a venv
```

## 3. Run everything

```bash
./run_all.sh
```

To use a specific interpreter (e.g. the venv above):

```bash
PYTHON=.venv/bin/python ./run_all.sh
```

The script runs the steps in dependency order and prints `==> [step]` as it
goes. `csn_powerlaw.py` is the slow step (KS-optimised fits over ~770k offshore
officers, a few minutes); everything else is seconds.

## 4. Pipeline steps and what they produce

Each script reads from `data/` and writes to `output/` (JSON/CSV) or
`output/figures/` (PNG). `make_figures.py` must run last.

| # | Script | Produces |
|---|--------|----------|
| 0 | `check_data.py`           | (integrity gate; verifies `data/` against `data/SHA256SUMS`) |
| 1 | `probe_a_sentinel.py`      | `probe_a_sentinel.json` |
| 2 | `probe_a_imputation.py`    | `probe_a_imputation.json` |
| 3 | `probe_b_within_us.py`     | `probe_b_within_us.json` (+`_points.csv`) |
| 4 | `probe_b_power.py`         | `probe_b_power.json` |
| 5 | `probe_b_cross_country.py` | `probe_b_cross_country.json` |
| 6 | `probe_c_interlock.py`     | `probe_c_interlock.json`, `fig_interlock_ccdf.csv` |
| 7 | `probe_d_place_decoupling.py` | `probe_d_place_decoupling.json` (+`_points.csv`) |
| 8 | `opacity_concentration.py` | `opacity_concentration.json`, `fig_{officer,intermediary}_ccdf.csv` |
| 9 | `opacity_by_jurisdiction.py` | `opacity_by_jurisdiction.json`, `opacity_by_source.csv` |
| 10 | `opacity_disentangle.py`   | `opacity_disentangle.json` |
| 11 | `hierarchical_icc.py`     | `hierarchical_icc.json` |
| 12 | `csn_powerlaw.py`         | `csn_powerlaw.json` |
| 13 | `make_figures.py`         | `output/figures/fig1-4.png` |

`scripts/_paths.py` defines the shared `ROOT/DATA/OUT/FIG` paths; every script
imports from it, so they work regardless of the current directory.

## 5. Data and integrity

The inputs are treated as immutable and pinned by SHA-256 in
[`data/SHA256SUMS`](data/SHA256SUMS) (documented in [MANIFEST.md](MANIFEST.md)).
`scripts/check_data.py` runs first in `./run_all.sh` and aborts if any input is
missing, altered, or added, so a changed file can never silently affect the
results. To verify on demand:

```bash
python3 scripts/check_data.py        # → "OK: 13 data files match data/SHA256SUMS."
```

`data/` contains all inputs (public sources, no proprietary data):

- `wid_individual_atoms.csv` — World Inequality Database income atoms
  (country × decile).
- `cz_mobility.xlsx`, `tract_outcomes_simple.csv` — Opportunity Insights
  commuting-zone rank-rank slopes and the Opportunity Atlas tract file.
- `corporate_directors/` — Financial Times 2016 director-company board graph
  (`nodes.csv`, `edges.csv`).
- `offshore_leaks/` — ICIJ Offshore Leaks database (`relationships.csv`,
  `nodes-*.csv`; version generated 2025-03-31).

### Two large inputs are not in the Git repository

Two ICIJ files exceed GitHub's 100 MB per-file limit and are therefore excluded
from version control (see `.gitignore`):

| File | Size |
|---|---:|
| `data/offshore_leaks/relationships.csv` | ~248 MB |
| `data/offshore_leaks/nodes-entities.csv` | ~190 MB |

A fresh clone will be missing them, and `scripts/check_data.py` will report them
as `MISSING`. They are public and immutable. Get the ICIJ Offshore Leaks
Database archive (snapshot generated 2025-03-31) from
<https://offshoreleaks.icij.org/pages/database>, then run the helper script,
which extracts just these two files and verifies them against `SHA256SUMS`:

```bash
# from an already-downloaded ICIJ full-CSV zip:
ICIJ_ZIP=/path/to/icij-offshoreleaks.zip ./data/download_large_files.sh
# or from a download URL:
ICIJ_URL='https://.../full-oldb.LATEST.zip' ./data/download_large_files.sh
```

Then confirm the integrity gate passes:

```bash
python3 scripts/check_data.py        # → "OK: 13 data files match data/SHA256SUMS."
```

The SHA-256 digests in [`data/SHA256SUMS`](data/SHA256SUMS) /
[MANIFEST.md](MANIFEST.md) pin the exact expected contents, so a correct
download is verified automatically.

## 6. Verifying the numbers

The pipeline is deterministic (fixed seeds where randomness is used, e.g. the
country cluster bootstrap in `hierarchical_icc.py` uses seed 0). Re-running
`./run_all.sh` yields identical values in `output/`.
