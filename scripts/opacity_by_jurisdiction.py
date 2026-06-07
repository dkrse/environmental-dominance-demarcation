"""Opacity, part 2: beneficial-ownership recording by jurisdiction and source.
Reads data/offshore_leaks/{relationships.csv,nodes-entities.csv}.
Writes output/opacity_by_jurisdiction.json + output/opacity_by_source.csv (for figure)."""


import os, json
import pandas as pd, numpy as np
from _paths import DATA, OUT

D = os.path.join(DATA, 'offshore_leaks')
ent = pd.read_csv(os.path.join(D, 'nodes-entities.csv'),
                  usecols=['node_id', 'jurisdiction_description', 'sourceID'], dtype=str)
juris = dict(zip(ent['node_id'], ent['jurisdiction_description'].fillna('NA')))
esrc  = dict(zip(ent['node_id'], ent['sourceID'].fillna('NA')))

r = pd.read_csv(os.path.join(D, 'relationships.csv'),
                usecols=['node_id_start', 'node_id_end', 'rel_type', 'link', 'sourceID'], dtype=str)
oo = r[r['rel_type'] == 'officer_of'].copy()
oo['juris'] = oo['node_id_end'].map(juris).fillna('NA')
# "source" = the entity's leak/provider = the recording regime (carries the 0%/99% bimodality;
# the relationship's own sourceID is coarser and mostly NA for the Pandora reconstructions).
oo['src']   = oo['node_id_end'].map(esrc).fillna('NA')
oo['ubo']   = oo['link'].str.lower().fillna('').str.contains('beneficial')

secrecy = {'British Virgin Islands','Cayman Islands','Bermuda','Bahamas','Panama','Jersey',
 'Guernsey','Isle of Man','Seychelles','Samoa','Cook Islands','Belize','Mauritius','Anguilla',
 'Saint Kitts and Nevis','Nevis','Marshall Islands','Niue','Gibraltar','Malta','Liechtenstein',
 'Luxembourg','Hong Kong','Singapore','Barbados','Aruba','Curacao'}
oo['secrecy'] = oo['juris'].isin(secrecy)

by_src = oo.groupby('src')['ubo'].agg(n='size', ubo_rate=lambda s: 100 * s.mean()).sort_values('ubo_rate', ascending=False)
by_src.reset_index().to_csv(os.path.join(OUT, 'opacity_by_source.csv'), index=False)

# Recording rate by entity jurisdiction (so the registry-end of the bimodality
# -- e.g. the Malta public register at 0% -- is itself recomputable, not a bare
# number in the text). Sorted by link count; full table written to CSV.
by_jur = oo.groupby('juris')['ubo'].agg(n='size', ubo_rate=lambda s: 100 * s.mean()).sort_values('n', ascending=False)
by_jur.reset_index().to_csv(os.path.join(OUT, 'opacity_by_jurisdiction.csv'), index=False)
malta = by_jur.loc['Malta'] if 'Malta' in by_jur.index else None

out = {
    'overall_ubo_pct': float(100 * oo['ubo'].mean()),
    'secrecy_ubo_pct': float(100 * oo[oo['secrecy']]['ubo'].mean()),
    'nonsecrecy_ubo_pct': float(100 * oo[~oo['secrecy']]['ubo'].mean()),
    'maskable_roles_pct': float(100 * oo['link'].str.lower().fillna('').str.contains('shareholder|director|secretary|nominee').mean()),
    'malta_registry': None if malta is None else {'n': int(malta['n']), 'ubo_rate': float(malta['ubo_rate'])},
    'top_sources': by_src.head(12).round(2).to_dict('index'),
    'top_jurisdictions': by_jur.head(12).round(4).to_dict('index'),
}
with open(os.path.join(OUT, 'opacity_by_jurisdiction.json'), 'w') as f:
    json.dump(out, f, indent=2, default=str)
print(json.dumps(out, indent=2, default=str))
