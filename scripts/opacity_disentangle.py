"""Opacity, part 3: eta^2 decomposition of beneficial-ownership recording.
Reads data/offshore_leaks/{relationships.csv,nodes-entities.csv}.
Writes output/opacity_disentangle.json."""


import os, json
import pandas as pd, numpy as np
from _paths import DATA, OUT

D = os.path.join(DATA, 'offshore_leaks')
ent = pd.read_csv(os.path.join(D, 'nodes-entities.csv'),
                  usecols=['node_id', 'jurisdiction_description', 'sourceID'], dtype=str)
juris = dict(zip(ent['node_id'], ent['jurisdiction_description'].fillna('NA')))
esrc  = dict(zip(ent['node_id'], ent['sourceID'].fillna('NA')))

r = pd.read_csv(os.path.join(D, 'relationships.csv'),
                usecols=['node_id_start', 'node_id_end', 'rel_type', 'link'], dtype=str)
oo = r[r['rel_type'] == 'officer_of'].copy()
oo['juris'] = oo['node_id_end'].map(juris).fillna('NA')
# source = entity's recording regime (see opacity_by_jurisdiction.py)
oo['src'] = oo['node_id_end'].map(esrc).fillna('NA')
oo['y'] = oo['link'].str.lower().fillna('').str.contains('beneficial').astype(float)

ybar = oo['y'].mean(); SST = ((oo['y'] - ybar) ** 2).sum()
def eta2(cols):
    g = oo.groupby(cols)['y']
    return float((g.size() * (g.mean() - ybar) ** 2).sum() / SST)

e_src, e_jur, e_cell = eta2('src'), eta2('juris'), eta2(['src', 'juris'])
out = {
    'N': int(len(oo)), 'overall_ubo_pct': float(100 * ybar),
    'eta2_source': e_src, 'eta2_jurisdiction': e_jur, 'eta2_cells': e_cell,
    'jurisdiction_after_source': e_cell - e_src,
    'source_after_jurisdiction': e_cell - e_jur,
}
with open(os.path.join(OUT, 'opacity_disentangle.json'), 'w') as f:
    json.dump(out, f, indent=2)
print(json.dumps(out, indent=2))
