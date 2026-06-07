"""Clauset--Shalizi--Newman power-law assessment for the three positional
networks. Replaces the fixed-quantile Hill exponent with a KS-optimised xmin,
an MLE alpha with its standard error, and likelihood-ratio tests of the
power law against log-normal and exponential alternatives (the Broido--Clauset
'scale-free?' protocol). Writes output/csn_powerlaw.json.

Degree sequences are rebuilt exactly as in probe_c_interlock.py and
opacity_concentration.py so the alpha values are comparable."""


import os, json, warnings
import pandas as pd, numpy as np
import powerlaw
from _paths import DATA, OUT

warnings.filterwarnings('ignore')

def interlock_degrees():
    D = os.path.join(DATA, 'corporate_directors')
    nodes = pd.read_csv(os.path.join(D, 'nodes.csv'), low_memory=False)
    nodes.columns = [c.strip().lstrip('# ').strip() for c in nodes.columns]
    nodes = nodes.rename(columns={'index': 'idx'})
    edges = pd.read_csv(os.path.join(D, 'edges.csv')); edges.columns = ['source', 'target']
    typ = dict(zip(nodes['idx'], nodes['type']))
    s = edges['source'].map(typ)
    person  = np.where(s.values == 'Person', edges['source'].values, edges['target'].values)
    company = np.where(s.values == 'Person', edges['target'].values, edges['source'].values)
    bp = pd.DataFrame({'person': person, 'company': company})
    bsize = bp.groupby('company').size()
    bp['bsm1'] = bp['company'].map(bsize) - 1
    il = bp.groupby('person')['bsm1'].sum()
    return il[il > 0].values.astype(float)

def rel_degrees(rel):
    r = pd.read_csv(os.path.join(DATA, 'offshore_leaks', 'relationships.csv'),
                    usecols=['node_id_start', 'rel_type'], dtype=str)
    deg = r[r['rel_type'] == rel].groupby('node_id_start').size()
    return deg[deg > 0].values.astype(float)

def csn(x):
    fit = powerlaw.Fit(x, discrete=True, verbose=False)
    out = {
        'n': int(len(x)),
        'xmin': float(fit.power_law.xmin),
        'n_tail': int((x >= fit.power_law.xmin).sum()),
        'alpha': float(fit.power_law.alpha),
        'alpha_se': float(fit.power_law.sigma),
        'ks_D': float(fit.power_law.D),
    }
    for alt in ('lognormal', 'exponential'):
        R, p = fit.distribution_compare('power_law', alt, normalized_ratio=True)
        out[f'LR_vs_{alt}'] = float(R)
        out[f'p_vs_{alt}'] = float(p)
    # Verdict: power law is the better description only if it is not beaten by
    # log-normal (R>=0 or the comparison is inconclusive at p>=0.05).
    pl_beaten = (out['LR_vs_lognormal'] < 0) and (out['p_vs_lognormal'] < 0.05)
    out['power_law_favoured_over_lognormal'] = (not pl_beaten)
    return out

res = {
    'interlock':       csn(interlock_degrees()),
    'officer_of':      csn(rel_degrees('officer_of')),
    'intermediary_of': csn(rel_degrees('intermediary_of')),
}
with open(os.path.join(OUT, 'csn_powerlaw.json'), 'w') as f:
    json.dump(res, f, indent=2)
print(json.dumps(res, indent=2))
