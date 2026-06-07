"""Probe A counterweight: the sentinel atoms are not bad data but genuine
near-zero incomes. Rather than only *removing* them, re-decompose under a
defensible *imputation* at the smallest genuine value in the data, to show the
headline is sensitive to the *treatment* of the zeros, not that they must be
dropped. Reads data/wid_individual_atoms.csv; writes output/probe_a_imputation.json."""


import os, json
import pandas as pd, numpy as np
from _paths import DATA, OUT

d = pd.read_csv(os.path.join(DATA, 'wid_individual_atoms.csv'))
w = 'weight'

def decomp(df):
    mu = np.average(df['ln_rho_eff'], weights=df[w])
    cm = df.groupby('iso3').apply(lambda g: np.average(g['ln_rho_eff'], weights=g[w])).rename('mu_c')
    Wc = df.groupby('iso3')[w].sum().rename('Wc')
    cc = pd.concat([cm, Wc], axis=1)
    Vb = np.average((cc['mu_c'] - mu) ** 2, weights=cc['Wc'])
    df = df.merge(cm, left_on='iso3', right_index=True)
    Vw = np.average((df['ln_rho_eff'] - df['mu_c']) ** 2, weights=df[w])
    return float(Vb), float(Vw), float(Vb + Vw)

sent = d['ln_rho_eff'] < -17
# smallest genuine (non-sentinel) value in the data
floor = float(d.loc[~sent, 'ln_rho_eff'].min())

a = decomp(d)                       # raw sentinels at -17.73
b = decomp(d[~sent])               # sentinels removed
di = d.copy()
di.loc[sent, 'ln_rho_eff'] = floor  # sentinels imputed at genuine floor
c = decomp(di)

res = {
    'genuine_floor': floor,
    'with_sentinels':    {'between': a[0], 'within': a[1], 'total': a[2]},
    'imputed_at_floor':  {'between': c[0], 'within': c[1], 'total': c[2]},
    'without_sentinels': {'between': b[0], 'within': b[1], 'total': b[2]},
    'published_within': 3.289,
    'within_range_low': min(a[1], b[1], c[1]),
    'within_range_high': max(a[1], b[1], c[1]),
}
with open(os.path.join(OUT, 'probe_a_imputation.json'), 'w') as f:
    json.dump(res, f, indent=2)
print(json.dumps(res, indent=2))
