"""Generate paper figures from output/ artifacts into output/figures/.
Run after the probe + opacity scripts."""

import os, json
import pandas as pd, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from _paths import OUT, FIG

def load(name):
    with open(os.path.join(OUT, name)) as f:
        return json.load(f)

# ---- Figure 1: visible vs hidden degree distribution (log-log CCDF) ----
conc = load('opacity_concentration.json')
ic   = load('probe_c_interlock.json')
# Intermediary layer omitted from the main figure: it is a selection artifact of
# which providers were leaked (see Caveats) and would muddy the visible-vs-hidden
# contrast the argument actually needs. It is reported only in the CSN table.
series = [
    ('fig_interlock_ccdf.csv',    f"board interlocks (visible), $\\alpha$={ic['hill_alpha']:.2f}",          'tab:blue'),
    ('fig_officer_ccdf.csv',      f"offshore officers (hidden), $\\alpha$={conc['officer_of']['hill_alpha']:.2f}",      'tab:red'),
]
plt.figure(figsize=(6.4, 4.6))
for fn, lab, col in series:
    df = pd.read_csv(os.path.join(OUT, fn))
    df = df[df['degree'] > 0]
    plt.loglog(df['degree'], df['ccdf'], '.', ms=3, color=col, label=lab)
plt.xlabel('degree / positional centrality')
plt.ylabel('CCDF  $P(X \\geq x)$')
plt.title('Visible vs hidden power layer: tail of the centrality distribution')
plt.legend(fontsize=8, frameon=False)
plt.tight_layout()
plt.savefig(os.path.join(FIG, 'fig1_distributions.png'), dpi=150)
plt.close()

# ---- Figure 2: bimodal opacity — beneficial-ownership recording by source ----
src = pd.read_csv(os.path.join(OUT, 'opacity_by_source.csv'), keep_default_na=False)
src['n'] = pd.to_numeric(src['n'])
src['ubo_rate'] = pd.to_numeric(src['ubo_rate'])
src = src[(src['n'] >= 1000) & (~src['src'].isin(['NA', 'nan', '']))].sort_values('ubo_rate')
plt.figure(figsize=(7.2, 5.0))
colors = ['tab:red' if v < 5 else ('tab:green' if v > 80 else 'tab:gray') for v in src['ubo_rate']]
plt.barh(range(len(src)), src['ubo_rate'], color=colors)
plt.yticks(range(len(src)), [str(s)[:42] for s in src['src']], fontsize=7)
plt.xlabel('ultimate-beneficial-owner recording rate (%)')
overall = load('opacity_by_jurisdiction.json')['overall_ubo_pct']
plt.axvline(overall, color='k', ls='--', lw=1, label=f'overall {overall:.2f}%')
plt.title('Opacity is bimodal: registries ~0%, leaked internal files ~99%', fontsize=11)
plt.legend(fontsize=8, frameon=False, loc='lower right')
plt.tight_layout()
plt.savefig(os.path.join(FIG, 'fig2_opacity_by_source.png'), dpi=150)
plt.close()

# ---- Figure 3: eta^2 — opacity attribution is confounded ----
dis = load('opacity_disentangle.json')
labels = ['source\nalone', 'jurisdiction\nalone', 'source x juris\n(cells)',
          'jurisdiction\nafter source', 'source\nafter jurisdiction']
vals = [dis['eta2_source'], dis['eta2_jurisdiction'], dis['eta2_cells'],
        dis['jurisdiction_after_source'], dis['source_after_jurisdiction']]
plt.figure(figsize=(6.8, 4.4))
bars = plt.bar(range(5), [100 * v for v in vals],
               color=['tab:blue', 'tab:orange', 'tab:purple', 'tab:orange', 'tab:blue'])
plt.xticks(range(5), labels, fontsize=8)
plt.ylabel('variance explained ($\\eta^2$, %)')
for b, v in zip(bars, vals):
    plt.text(b.get_x() + b.get_width() / 2, 100 * v + 1, f'{100*v:.1f}', ha='center', fontsize=8)
plt.title('Opacity is a recording-regime property: jurisdiction adds 1% after source', fontsize=11)
plt.tight_layout()
plt.savefig(os.path.join(FIG, 'fig3_eta2.png'), dpi=150)
plt.close()

# ---- Figure 4: Probe D — causal place effect at a fixed parental rank ----
pd_ = load('probe_d_place_decoupling.json')
pts = pd.read_csv(os.path.join(OUT, 'probe_d_place_decoupling_points.csv'))
x = pd.to_numeric(pts['kfr_pooled_pooled_p25'], errors='coerce')
w = pd.to_numeric(pts['pooled_pooled_count'], errors='coerce')
m = x.notna() & w.notna() & (x > 0) & (x < 1) & (w > 0)
x, w = x[m].values, w[m].values
plt.figure(figsize=(6.8, 4.4))
plt.hist(x, bins=80, weights=w, color='tab:green', alpha=0.8)
for q, lab, c in [(pd_['place_effect_p10'], 'P10', 'tab:gray'),
                  (pd_['mean_child_rank_at_p25'], 'mean', 'k'),
                  (pd_['place_effect_p90'], 'P90', 'tab:gray')]:
    plt.axvline(q, color=c, ls='--', lw=1.2,
                label=f"{lab} = {q:.2f}" if lab == 'mean' else None)
plt.annotate('', xy=(pd_['place_effect_p10'], plt.ylim()[1]*0.9),
             xytext=(pd_['place_effect_p90'], plt.ylim()[1]*0.9),
             arrowprops=dict(arrowstyle='<->', color='tab:gray'))
plt.text((pd_['place_effect_p10']+pd_['place_effect_p90'])/2, plt.ylim()[1]*0.93,
         f"P10-P90 = {pd_['place_effect_p10_p90_gap_pts']:.0f} rank pts",
         ha='center', fontsize=9, color='tab:gray')
plt.xlabel("child's adult income rank at parental rank p25 (causal place effect)")
plt.ylabel('population weight')
plt.title(f"Environment moves outcomes at a fixed start "
          f"(reliability {pd_['reliability']*100:.0f}%)", fontsize=11)
plt.legend(fontsize=8, frameon=False, loc='upper right')
plt.tight_layout()
plt.savefig(os.path.join(FIG, 'fig4_place_decoupling.png'), dpi=150)
plt.close()

print('figures written to', FIG)
print(os.listdir(FIG))
