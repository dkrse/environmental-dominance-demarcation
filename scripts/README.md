# Pipeline

Run from project root with the venv: `../.venv/bin/python scripts/<name>.py`,
or run the whole thing in dependency order with `./run_all.sh`.
Each script reads from `data/` and writes JSON/CSV to `output/` (figures to
`output/figures/`). Run `make_figures.py` last.

| order | script | reads | writes |
|---|---|---|---|
| 0 | `check_data.py`             | data/SHA256SUMS | (integrity gate; verifies data/) |
| 1 | `probe_a_sentinel.py`       | wid_individual_atoms.csv | probe_a_sentinel.json |
| 2 | `probe_a_imputation.py`     | wid_individual_atoms.csv | probe_a_imputation.json |
| 3 | `probe_b_within_us.py`      | cz_mobility.xlsx, tract_outcomes_simple.csv | probe_b_within_us.json (+_points.csv) |
| 4 | `probe_b_power.py`          | output/probe_b_within_us.json | probe_b_power.json |
| 5 | `probe_b_cross_country.py`  | wid_individual_atoms.csv | probe_b_cross_country.json |
| 6 | `probe_c_interlock.py`      | corporate_directors/ | probe_c_interlock.json, fig_interlock_ccdf.csv |
| 7 | `probe_d_place_decoupling.py` | tract_outcomes_simple.csv | probe_d_place_decoupling.json (+_points.csv) |
| 8 | `opacity_concentration.py`  | offshore_leaks/relationships.csv | opacity_concentration.json, fig_{officer,intermediary}_ccdf.csv |
| 9 | `opacity_by_jurisdiction.py`| offshore_leaks/ | opacity_by_jurisdiction.json, opacity_by_source.csv |
| 10 | `opacity_disentangle.py`   | offshore_leaks/ | opacity_disentangle.json |
| 11 | `hierarchical_icc.py`      | wid_individual_atoms.csv | hierarchical_icc.json |
| 12 | `csn_powerlaw.py`          | corporate_directors/, offshore_leaks/relationships.csv | csn_powerlaw.json |
| 13 | `make_figures.py`          | output/*.json, *.csv | figures/fig1–4.png |

`_paths.py` defines ROOT/DATA/OUT/FIG. "source" in the opacity scripts means the **entity's**
leak/provider (the recording regime), not the relationship's sourceID.
`csn_powerlaw.py` is the slow step (a few minutes); everything else takes seconds.
