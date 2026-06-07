"""Opacity, part 1: concentration of the hidden offshore layer.
Reads data/offshore_leaks/relationships.csv.
Writes output/opacity_concentration.json + output/fig_{officer,intermediary}_ccdf.csv."""


import os, json
import pandas as pd, numpy as np
from _paths import DATA, OUT

D = os.path.join(DATA, 'offshore_leaks')
r = pd.read_csv(os.path.join(D, 'relationships.csv'),
                usecols=['node_id_start', 'node_id_end', 'rel_type'], dtype=str)

def concentration(rel, fig_name):
    deg = r[r['rel_type'] == rel].groupby('node_id_start').size()
    deg = deg[deg > 0]
    x = deg.values.astype(float); lx = np.log(x)
    xs = np.sort(x); t = xs[xs >= np.quantile(xs, 0.95)]; xmin = t.min()
    alpha = 1 + len(t) / np.sum(np.log(t / xmin))
    srt = deg.sort_values(ascending=False)
    res = {
        'actors': int(len(deg)), 'max': int(x.max()),
        'var_ln_degree': float(lx.var()),
        'top1pct_share': float(100 * srt.head(max(1, int(.01 * len(deg)))).sum() / deg.sum()),
        'top01pct_share': float(100 * srt.head(max(1, int(.001 * len(deg)))).sum() / deg.sum()),
        'hill_alpha': float(alpha),
    }
    vals, cnts = np.unique(x.astype(int), return_counts=True)
    ccdf = 1 - np.cumsum(cnts) / cnts.sum() + cnts / cnts.sum()
    pd.DataFrame({'degree': vals, 'ccdf': ccdf}).to_csv(os.path.join(OUT, f'fig_{fig_name}_ccdf.csv'), index=False)
    return res

out = {
    'officer_of':      concentration('officer_of', 'officer'),
    'intermediary_of': concentration('intermediary_of', 'intermediary'),
}
for k in ('officer_of', 'intermediary_of'):
    V = out[k]['var_ln_degree']
    out[k]['R_net'] = {'0.0324': V / 0.0324, '0.16': V / 0.16}
with open(os.path.join(OUT, 'opacity_concentration.json'), 'w') as f:
    json.dump(out, f, indent=2)
print(json.dumps(out, indent=2))
