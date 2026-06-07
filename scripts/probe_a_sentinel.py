"""Probe A: leverage of 12 sentinel atoms on the within-country variance component.
Reads data/wid_individual_atoms.csv; writes output/probe_a_sentinel.json."""

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
bad_countries = sorted(d.loc[sent, 'iso3'].unique().tolist())
a = decomp(d)
b = decomp(d[~sent])
res = {
    'n_sentinels': int(sent.sum()),
    'sentinel_countries': bad_countries,
    'sentinel_weight_share_pct': float(100 * d[sent][w].sum() / d[w].sum()),
    'with_sentinels':    {'between': a[0], 'within': a[1], 'total': a[2]},
    'without_sentinels': {'between': b[0], 'within': b[1], 'total': b[2]},
    'within_inflation': a[1] - b[1],
    'within_inflation_pct': float(100 * (a[1] - b[1]) / a[1]),
    'published_within': 3.289,
}
with open(os.path.join(OUT, 'probe_a_sentinel.json'), 'w') as f:
    json.dump(res, f, indent=2)
print(json.dumps(res, indent=2))
