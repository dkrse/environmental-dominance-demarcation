# The Measurement Limit of Environmental Dominance

Reproduction code and data for the paper:

> **The Measurement Limit of Environmental Dominance: Why the Strong Thesis Can
> Be Neither Confirmed nor Refuted, and What Holds Instead**
> Kristian Sestak (Independent Researcher).
> [ORCID 0009-0002-1455-5915](https://orcid.org/0009-0002-1455-5915).

The paper sources (`paper/paper.tex`, `paper/paper.pdf`) and every number,
table value and figure in them are recomputed from the raw inputs in `data/`
by the scripts in `scripts/`. The full pipeline runs in a few minutes on a
laptop and is deterministic.

## What the project does

Two companion papers argue that *environment* dominates an entity's
*capability* because the variance of favourable possibilities exceeds the
variance of capability. This repository tests that claim. It distinguishes a
**weak** reading (resource/positional dispersion exceeds capability dispersion)
from a **strong** reading (environment causally dominates capability), and uses
four independent empirical probes plus an opacity analysis to show that the weak
reading holds while the strong reading is, on available data, *structurally
unmeasurable* rather than merely unproven.

The probes draw on public data:

- **Probe A** — sentinel-atom leverage and an imputation counterweight on the
  income variance decomposition (World Inequality Database).
- **Probe B** — the environment→mobility transmission-law slope, within the US
  (Opportunity Insights) and cross-country (WID), with a power analysis.
- **Probe C** — concentration of the *visible* board-interlock network
  (Financial Times 2016 director-company graph): a power-law test.
- **Probe D** — the causal place effect at fixed parental rank (Opportunity
  Atlas), decoupling place from starting line.
- **Opacity** — degree concentration, beneficial-ownership recording rates,
  jurisdiction-vs-source variance decomposition and Clauset–Shalizi–Newman
  power-law fits over the ICIJ Offshore Leaks network.

## Layout

```
data/        immutable public inputs, pinned by SHA-256 (see MANIFEST.md)
scripts/     analysis pipeline (one script per step) + check_data.py
output/      computed results (JSON/CSV) and output/figures/ (PNG)
paper/       LaTeX source and compiled PDF
run_all.sh   runs the whole pipeline in dependency order
```

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./run_all.sh
```

To use a specific interpreter: `PYTHON=.venv/bin/python ./run_all.sh`.

The pipeline first runs `scripts/check_data.py`, an integrity gate that aborts
if any input in `data/` differs from `data/SHA256SUMS`, so a changed input can
never silently affect the results. `csn_powerlaw.py` is the slow step (a few
minutes); everything else takes seconds. A clean data check prints
`OK: 13 data files match data/SHA256SUMS.`

See **[INSTALL.md](INSTALL.md)** for full prerequisites, the per-step table of
what each script produces, and reproduction details, and **[MANIFEST.md](MANIFEST.md)**
for the data sources and integrity hashes.

## Requirements

Python ≥ 3.10 (developed on 3.12) and the packages pinned in
[`requirements.txt`](requirements.txt): `pandas`, `numpy`, `scipy`,
`matplotlib`, `openpyxl`, `powerlaw`. All inputs ship in `data/`; no network
access or proprietary sources are needed.

## Data

All inputs are public (WID, Opportunity Insights, the Financial Times 2016
board-interlock graph via Netzschleuder, and the ICIJ Offshore Leaks Database
snapshot of 2025-03-31). They are treated as immutable and documented, with
SHA-256 digests, in [MANIFEST.md](MANIFEST.md).

## License

Released under the [MIT License](LICENSE). © 2026 krse (Kristian Sestak).

## Author

**krse** (Kristian Sestak) — kristian.sestak@gmail.com
