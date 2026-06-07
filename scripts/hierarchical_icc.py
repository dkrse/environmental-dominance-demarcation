"""Hierarchical (ICC-style) decomposition of Var(ln rho_eff) into the share
borne between countries vs. between classes within a country. Turns the two bare
variance components into a tangible statement and a country-level ICC, with a
country cluster-bootstrap CI. Reads data/wid_individual_atoms.csv on the
sentinel-free atoms (so the share is not propped by the clipped zeros);
writes output/hierarchical_icc.json."""


import os, json
import pandas as pd, numpy as np
from _paths import DATA, OUT

d = pd.read_csv(os.path.join(DATA, 'wid_individual_atoms.csv'))
d = d[d['ln_rho_eff'] > -17].copy()   # drop sentinel clips (see Probe A)
w = 'weight'

def shares(df):
    mu = np.average(df['ln_rho_eff'], weights=df[w])
    cm = df.groupby('iso3').apply(lambda g: np.average(g['ln_rho_eff'], weights=g[w])).rename('mu_c')
    Wc = df.groupby('iso3')[w].sum().rename('Wc')
    cc = pd.concat([cm, Wc], axis=1)
    Vb = np.average((cc['mu_c'] - mu) ** 2, weights=cc['Wc'])
    dd = df.merge(cm, left_on='iso3', right_index=True)
    Vw = np.average((dd['ln_rho_eff'] - dd['mu_c']) ** 2, weights=dd[w])
    Vt = Vb + Vw
    return Vb, Vw, Vt, Vb / Vt

Vb, Vw, Vt, icc = shares(d)

# Country cluster bootstrap: resample whole countries with replacement.
rng = np.random.default_rng(0)
countries = d['iso3'].unique()
B = 1000
iccs = []
for _ in range(B):
    pick = rng.choice(countries, size=len(countries), replace=True)
    rep = pd.concat([d[d['iso3'] == c].assign(iso3=f'{c}_{i}') for i, c in enumerate(pick)])
    iccs.append(shares(rep)[3])
lo, hi = np.percentile(iccs, [2.5, 97.5])

res = {
    'basis': 'sentinel-free atoms',
    'V_between': float(Vb), 'V_within': float(Vw), 'V_total': float(Vt),
    'share_between_pct': float(100 * icc),
    'share_within_pct': float(100 * (1 - icc)),
    'icc_country': float(icc),
    'icc_country_ci95': [float(lo), float(hi)],
    'n_countries': int(len(countries)),
}
with open(os.path.join(OUT, 'hierarchical_icc.json'), 'w') as f:
    json.dump(res, f, indent=2)
print(json.dumps(res, indent=2))
