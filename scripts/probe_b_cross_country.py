"""Probe B (supporting): cross-country transmission-law test with Corak IGE.
Reads data/wid_individual_atoms.csv; writes output/probe_b_cross_country.json."""

import os, json
import pandas as pd, numpy as np
from scipy import stats
from _paths import DATA, OUT

d = pd.read_csv(os.path.join(DATA, 'wid_individual_atoms.csv'))
V = d.groupby('iso3')['ln_rho_eff'].var(ddof=0).rename('V_c').reset_index()

corak = {'DNK':0.15,'NOR':0.17,'FIN':0.18,'CAN':0.19,'AUS':0.26,'SWE':0.27,'NZL':0.29,
 'DEU':0.32,'JPN':0.34,'ESP':0.40,'FRA':0.41,'SGP':0.44,'USA':0.47,'CHE':0.46,
 'PAK':0.46,'ARG':0.49,'ITA':0.50,'GBR':0.50,'CHL':0.52,'BRA':0.58,'CHN':0.60,'PER':0.67}
cdf = pd.DataFrame(corak.items(), columns=['iso3', 'theta'])
m = cdf.merge(V, on='iso3').dropna()
m = m[m['V_c'] > 0].copy()
m['lnV'] = np.log(m['V_c']); m['x'] = -np.log(1 - m['theta'] ** 2)

def fit(mm):
    r = stats.linregress(mm['x'], mm['lnV']); df = len(mm) - 2
    p1 = float(2 * stats.t.sf(abs((r.slope - 1) / r.stderr), df))
    return {'n': int(len(mm)), 'slope': float(r.slope), 'r2': float(r.rvalue ** 2), 'p_slope_eq_1': p1}

contaminated = ['CHL', 'PER', 'BRA', 'ARG']  # WID bottom-decile share == 0 artifacts
out = {
    'all': fit(m),
    'drop_contaminated': fit(m[~m['iso3'].isin(contaminated)]),
    'theilsen_slope_all': float(stats.theilslopes(m['lnV'], m['x'])[0]),
    'spearman_theta_V': float(stats.spearmanr(m['theta'], m['V_c']).correlation),
    'spearman_p': float(stats.spearmanr(m['theta'], m['V_c']).pvalue),
    'contaminated_dropped': contaminated,
}
with open(os.path.join(OUT, 'probe_b_cross_country.json'), 'w') as f:
    json.dump(out, f, indent=2)
print(json.dumps(out, indent=2))
