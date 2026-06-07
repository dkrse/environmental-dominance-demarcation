# Data Manifest

This file pins the exact inputs the analysis depends on. Every file in `data/`
is fixed by its SHA-256 hash; the canonical, machine-readable list lives in
[`data/SHA256SUMS`](data/SHA256SUMS) and this document mirrors it for humans.

The inputs are treated as **immutable**. `scripts/check_data.py` runs as the
first step of `./run_all.sh` and aborts the pipeline if any file is missing,
altered, or added, so a changed input can never silently propagate into the
results.

## Files

Sizes in bytes; full SHA-256 digests (identical to `data/SHA256SUMS`).

| File (under `data/`) | Bytes | SHA-256 |
|---|---:|---|
| `corporate_directors/edges.csv` | 5506564 | `47867ad25255bfc0a3a35cbb695a5aaed4f08b17ccbc8e6c4b4763f6764a7dac` |
| `corporate_directors/gprops.csv` | 749 | `0942323d31ab63867128688c0dd2798344083f911523e1ae719fb902fae60cce` |
| `corporate_directors/nodes.csv` | 27340072 | `81b5218aba49bdb6f91d7a2ccd1c73b83c0c89081aa61f537f66ff72ecf2c71c` |
| `cz_mobility.xlsx` | 72170 | `41610bb259dcff44bba231c1ae20409b1feace0cbeaa0d3159ce2e149603aa85` |
| `offshore_leaks/GENERATED_ON_20250331.txt` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `offshore_leaks/nodes-addresses.csv` | 72465663 | `c24d66e198c87cbc09b8d56793c1c6bbbf070cdab04041608637c5e8ee1ccd04` |
| `offshore_leaks/nodes-entities.csv` | 198926104 | `5946fa549c8304cef02c03c536ae07bb8c784ab44d97eaf27075bf3cfcda71fa` |
| `offshore_leaks/nodes-intermediaries.csv` | 3944578 | `2ec43bb73da0b8ca58c476ecfb36c16fc4a30014f829f8cfec69f39cb6b3c397` |
| `offshore_leaks/nodes-officers.csv` | 91021122 | `ca63c1b23563012759402b79fa82e8ccd3cb8c61300193002b8f52c31fdf8e00` |
| `offshore_leaks/nodes-others.csv` | 398436 | `32f6532c8bb290233d67423de5d778cb5a55478e721d0a07e9c8a2991a1b82c0` |
| `offshore_leaks/relationships.csv` | 259198321 | `1363226ca173e8f26f4741504dd677fe44e941233af854ff03b45c99cbba2bb2` |
| `tract_outcomes_simple.csv` | 34406499 | `d246a041179cac832983f1814725e91c8f99adc41d31b06ee3ac9b4f662be10b` |
| `wid_individual_atoms.csv` | 289063 | `4ee301c46905667b53f827dfd38b75d368afa8cc84c93065264ccadb954976c7` |

(`offshore_leaks/GENERATED_ON_20250331.txt` is an empty marker file recording
the ICIJ database snapshot date; its hash is the canonical empty-file SHA-256.)

## Sources

All inputs are public; no proprietary or restricted data is used.

- `wid_individual_atoms.csv` — World Inequality Database income shares
  (country × decile), joined to World Bank GDP-per-capita and population.
- `cz_mobility.xlsx`, `tract_outcomes_simple.csv` — Opportunity Insights:
  commuting-zone rank-rank mobility slopes and the Opportunity Atlas tract file.
- `corporate_directors/` — Financial Times 2016 director-company board-interlock
  graph (via the Netzschleuder repository).
- `offshore_leaks/` — ICIJ Offshore Leaks Database, snapshot generated
  2025-03-31 (combined Panama, Paradise, Pandora, Bahamas and Offshore Leaks
  corpora).

## Verifying

```bash
python3 scripts/check_data.py        # portable, no dependencies
# or, with coreutils:
cd data && sha256sum -c SHA256SUMS
```

A clean run prints `OK: 13 data files match data/SHA256SUMS.`

## Regenerating the manifest (only when inputs intentionally change)

```bash
cd data && find . -type f ! -name SHA256SUMS | sort | sed 's|^\./||' \
  | xargs sha256sum > SHA256SUMS
```

Then update the table above to match. Do this **only** for a deliberate data
update — never to make a check pass after an accidental edit.
