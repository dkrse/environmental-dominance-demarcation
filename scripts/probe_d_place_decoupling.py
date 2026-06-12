"""Probe D: the place-decoupling test.

The three probes of the paper show the *strong* thesis cannot be pinned to a
directly measured quantity. This probe asks the complementary question with an
indirect, quasi-experimental design the series cites but never uses for this
purpose: does the environment causally move outcomes when the starting line is
held fixed?

The Opportunity Atlas column kfr_pooled_pooled_p25 is the *causal* effect of a
childhood place on a child's adult income RANK, estimated for children whose
parents sit at the SAME income rank (p25) via the Chetty-Hendren movers design.
Holding the parental rank fixed holds the family resource input -- and much of
any individual "capability" k that is inherited or family-mediated -- constant,
so cross-place variation is environment by construction, and causal rather than
selective.

What this probe CAN measure (cleanly):
  V_env = noise-corrected between-place variance of the causal place effect at a
          fixed parental rank. Reliability = V_env / (total cross-place var).

What this probe CANNOT measure, and says so:
  the capability term k. Recovering an individual within-cell SD from se*sqrt(n)
  fails a bound check: population income ranks are uniform by construction, so
  their total variance is exactly 1/12, and by the law of total variance the
  count-weighted average within-cell variance cannot exceed 1/12 (boundedness on
  [0,1] alone would only give 1/4); 'count' is not a raw n and the SEs are
  shrinkage-based. So no clean V_env / V_k dominance ratio can be formed -- the
  capability side resists measurement here exactly as it does everywhere else in
  the series. The probe therefore delivers a positive causal finding on the
  environment side, not a dominance ratio.

Reads data/tract_outcomes_simple.csv. Writes output/probe_d_place_decoupling.json
and output/probe_d_place_decoupling_points.csv.
"""



import os, json
import pandas as pd, numpy as np
from _paths import DATA, OUT

COL, SE, CNT = 'kfr_pooled_pooled_p25', 'kfr_pooled_pooled_p25_se', 'pooled_pooled_count'
RANK_VAR_MAX = 1.0 / 12.0  # population ranks are uniform by construction => total Var = 1/12;
                           # by the law of total variance the count-weighted average within-cell
                           # variance cannot exceed this (boundedness alone gives only 1/4)

t = pd.read_csv(os.path.join(DATA, 'tract_outcomes_simple.csv'))
d = t[[COL, SE, CNT, 'cz']].copy()
for c in (COL, SE, CNT):
    d[c] = pd.to_numeric(d[c], errors='coerce')
d = d[(d[COL] > 0) & (d[COL] < 1) & (d[CNT] >= 20) & (d[SE] > 0)].dropna()

x, s, w = d[COL].values, d[SE].values, d[CNT].values

# --- ENVIRONMENT side: between-place variance at a fixed parental rank ---------
mu = np.average(x, weights=w)
total_var = np.average((x - mu) ** 2, weights=w)   # raw cross-place dispersion
noise_var = np.average(s ** 2, weights=w)          # sampling noise
V_env = total_var - noise_var                      # reliable place (environment) variance
reliability = V_env / total_var

# interpretable spread of the causal place effect (count-weighted percentiles)
reps = np.clip((w / w.min()).astype(int), 1, 50)
xr = np.repeat(x, reps)
p10, p50, p90 = np.percentile(xr, [10, 50, 90])

# --- CAPABILITY side: attempted and rejected ----------------------------------
sd_child = s * np.sqrt(w)
# count-weighted average within-cell variance == E[Var(rank | cell)], which the
# law of total variance bounds by the total rank variance 1/12 (ranks uniform).
V_cap_naive = float(np.average(sd_child ** 2, weights=w))
cap_recoverable = bool(V_cap_naive <= RANK_VAR_MAX)  # total-variance bound, not boundedness

out = {
    'n_tracts': int(len(d)),
    'n_cz': int(d['cz'].nunique()),
    'parental_rank_held_fixed': 'p25',
    'mean_child_rank_at_p25': float(mu),
    'total_cross_place_var': float(total_var),
    'sampling_noise_var': float(noise_var),
    'V_env_reliable': float(V_env),
    'reliability': float(reliability),
    'sd_place_effect_rank': float(np.sqrt(V_env)),
    'place_effect_p10': float(p10),
    'place_effect_p50': float(p50),
    'place_effect_p90': float(p90),
    'place_effect_p10_p90_gap_pts': float((p90 - p10) * 100),
    'capability_side': {
        'V_cap_naive_se_sqrt_n': V_cap_naive,
        'rank_var_upper_bound': RANK_VAR_MAX,
        'recoverable': cap_recoverable,
        'note': ('population ranks are uniform => total variance 1/12; by the law '
                 'of total variance the count-weighted average within-cell variance '
                 'cannot exceed 1/12. se*sqrt(count) implies 0.187 > 1/12, so it does '
                 'not recover an individual capability SD; no clean V_env/V_k '
                 'dominance ratio can be formed.'),
    },
}

d[[COL, SE, CNT, 'cz']].to_csv(
    os.path.join(OUT, 'probe_d_place_decoupling_points.csv'), index=False)
with open(os.path.join(OUT, 'probe_d_place_decoupling.json'), 'w') as f:
    json.dump(out, f, indent=2)
print(json.dumps(out, indent=2))
