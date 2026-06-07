"""Probe B (primary): within-US transmission-law test, slope predicted = 1.
Reads data/cz_mobility.xlsx (Chetty RM) + data/tract_outcomes_simple.csv.
Writes output/probe_b_within_us.json and output/probe_b_within_us_points.csv."""

import os, json
import pandas as pd, numpy as np
from scipy import stats
from _paths import DATA, OUT

raw = pd.read_excel(os.path.join(DATA, 'cz_mobility.xlsx'), sheet_name=0, header=None)
cz = raw.iloc[14:].copy()
cz.columns = ['cz', 'czname', 'state', 'pop', 'RM', 'AM', 'PQ5Q1']
cz = cz[['cz', 'RM', 'pop']].dropna()
cz['cz'] = cz['cz'].astype(int)
cz['RM'] = pd.to_numeric(cz['RM'], errors='coerce')
cz['pop'] = pd.to_numeric(cz['pop'], errors='coerce')
cz = cz[(cz['RM'] > 0) & (cz['RM'] < 1)].dropna()

t = pd.read_csv(os.path.join(DATA, 'tract_outcomes_simple.csv'))
t['kfr'] = pd.to_numeric(t['kfr_pooled_pooled_p25'], errors='coerce')
t['cnt'] = pd.to_numeric(t['pooled_pooled_count'], errors='coerce')
t = t[(t['kfr'] > 0) & (t['kfr'] < 1)].dropna(subset=['kfr', 'cz', 'cnt'])
kbar = 50
t['rho'] = 1 - (1 - t['kfr']) ** (1 / kbar)
t['lnrho'] = np.log(t['rho'])

def wvar(g):
    w = g['cnt'].values; x = g['lnrho'].values
    if w.sum() <= 0 or len(x) < 10:
        return np.nan
    mu = np.average(x, weights=w)
    return np.average((x - mu) ** 2, weights=w)

agg = t.groupby('cz').apply(lambda g: pd.Series({'V': wvar(g), 'ntr': len(g)})).reset_index()
agg = agg[agg['ntr'] >= 20]
m = cz.merge(agg, on='cz').dropna()
m = m[m['V'] > 0].copy()
m['lnV'] = np.log(m['V'])
m['x'] = -np.log(1 - m['RM'] ** 2)
m[['cz', 'RM', 'V', 'ntr']].to_csv(os.path.join(OUT, 'probe_b_within_us_points.csv'), index=False)

res = stats.linregress(m['x'], m['lnV'])
df = len(m) - 2
t1 = (res.slope - 1) / res.stderr
p1 = float(2 * stats.t.sf(abs(t1), df))
ci = (res.slope - stats.t.ppf(.975, df) * res.stderr, res.slope + stats.t.ppf(.975, df) * res.stderr)
out = {
    'n_cz': int(len(m)),
    'slope': float(res.slope), 'slope_ci95': [float(ci[0]), float(ci[1])],
    'stderr': float(res.stderr), 'r2': float(res.rvalue ** 2),
    'intercept': float(res.intercept), 'implied_sigma_u2': float(np.exp(res.intercept)),
    'p_slope_eq_1': p1, 'p_slope_eq_0': float(res.pvalue),
    'spearman_RM_V': float(stats.spearmanr(m['RM'], m['V']).correlation),
}
with open(os.path.join(OUT, 'probe_b_within_us.json'), 'w') as f:
    json.dump(out, f, indent=2)
print(json.dumps(out, indent=2))
