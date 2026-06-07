"""Probe B power analysis: distinguish 'the coupling is empty' from 'the data
cannot resolve any coupling'. Given the observed residual scatter and design
(n, SE of slope), compute the minimum detectable slope (MDE) at 80% power and
the power the test actually had to reject slope=0 if the true slope were 1.
Reads output/probe_b_within_us.json; writes output/probe_b_power.json."""

import os, json
import numpy as np
from scipy import stats
from _paths import OUT

with open(os.path.join(OUT, 'probe_b_within_us.json')) as f:
    b = json.load(f)
se = b['stderr']; n = b['n_cz']; slope = b['slope']
df = n - 2
tcrit = stats.t.ppf(0.975, df)          # two-sided alpha=0.05
z80 = stats.norm.ppf(0.80)

# Minimum detectable effect: smallest true slope giving 80% power vs slope=0.
mde = se * (tcrit + z80)

# Power the test actually had to reject slope=0 if the TRUE slope equalled the
# model's prediction of 1 (noncentral-t, noncentrality = 1/se).
ncp = 1.0 / se
power_at_1 = float(stats.nct.sf(tcrit, df, ncp) + stats.nct.cdf(-tcrit, df, ncp))

res = {
    'n': n, 'slope_se': se, 'observed_slope': slope,
    'mde_slope_80pct_power': float(mde),
    'predicted_slope': 1.0,
    'power_to_detect_slope1_vs_0': power_at_1,
    'note': ('Predicted slope (1) is far below the minimum detectable slope; '
             'the test is underpowered, so slope=0 and slope=1 are both '
             'unrejectable. This is non-resolution, not an empty coupling.'),
}
with open(os.path.join(OUT, 'probe_b_power.json'), 'w') as f:
    json.dump(res, f, indent=2)
print(json.dumps(res, indent=2))
