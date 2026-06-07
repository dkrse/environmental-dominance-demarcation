"""Probe C: visible board-interlock network (Financial Times 2016).
Reads data/corporate_directors/{nodes.csv,edges.csv}.
Writes output/probe_c_interlock.json and output/fig_interlock_ccdf.csv."""


import os, json
import pandas as pd, numpy as np
from _paths import DATA, OUT

D = os.path.join(DATA, 'corporate_directors')
nodes = pd.read_csv(os.path.join(D, 'nodes.csv'), low_memory=False)
nodes.columns = [c.strip().lstrip('# ').strip() for c in nodes.columns]
nodes = nodes.rename(columns={'index': 'idx'})
edges = pd.read_csv(os.path.join(D, 'edges.csv'))
edges.columns = ['source', 'target']
typ = dict(zip(nodes['idx'], nodes['type']))

s = edges['source'].map(typ)
person  = np.where(s.values == 'Person', edges['source'].values, edges['target'].values)
company = np.where(s.values == 'Person', edges['target'].values, edges['source'].values)
bp = pd.DataFrame({'person': person, 'company': company})

board_size = bp.groupby('company').size()
bp['bsm1'] = bp['company'].map(board_size) - 1
interlock = bp.groupby('person')['bsm1'].sum()
interlock = interlock[interlock > 0]

x = interlock.values.astype(float); lx = np.log(x)
xs = np.sort(x)
tail = xs[xs >= np.quantile(xs, 0.95)]; xmin = tail.min()
alpha = 1 + len(tail) / np.sum(np.log(tail / xmin))
top1 = float(100 * interlock.sort_values(ascending=False).head(int(.01 * len(interlock))).sum() / interlock.sum())

Vc = float(lx.var())
out = {
    'n_directors': int((nodes['type'] == 'Person').sum()),
    'n_companies': int((nodes['type'] == 'Company').sum()),
    'n_edges': int(len(edges)),
    'var_ln_centrality': Vc,
    'top1pct_share': top1,
    'hill_alpha': float(alpha),
    'R_net': {'0.0324': Vc / 0.0324, '0.16': Vc / 0.16},
}
with open(os.path.join(OUT, 'probe_c_interlock.json'), 'w') as f:
    json.dump(out, f, indent=2)

# CCDF for figure (compact)
vals, cnts = np.unique(x.astype(int), return_counts=True)
ccdf = 1 - np.cumsum(cnts) / cnts.sum() + cnts / cnts.sum()
pd.DataFrame({'degree': vals, 'ccdf': ccdf}).to_csv(os.path.join(OUT, 'fig_interlock_ccdf.csv'), index=False)
print(json.dumps(out, indent=2))
