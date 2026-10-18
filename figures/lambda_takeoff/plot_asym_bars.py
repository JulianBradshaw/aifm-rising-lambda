# Takeoff at each Infinite Coding Labor Asymptote: λ 0.5, and λ 0.65 and λ 1
# with only the straightforward benefit switched. Coding Uplift anchor, Daniel 08/16/26.
import json, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
S, T1, T2, MUTED, GRID = '#fcfcfb', '#0b0b0b', '#52514e', '#8a8984', '#e6e5e0'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.edgecolor':MUTED,
  'axes.labelcolor':T2,'xtick.color':T2,'ytick.color':T2,'figure.facecolor':S,'axes.facecolor':S})
B = {(r['asymptote'], r['lam']): r['takeoff_months'] for r in json.load(open('asym_benefit_raw.json')) if r['mode'] == 'uplift-solved'}
F = {r['asymptote']: r['takeoff_months'] for r in json.load(open('asym_full_raw.json'))}
CAPS = [(15, '15×\n(default)'), (100, '100×'), (1e3, '1,000×'), (1e4, '10,000×'), (1e8, 'Effectively\nunbounded')]
SER = [('λ 0.5', '#8a8984', lambda c: B[(c, 0.5)]),
       ('λ 0.65, straightforward benefit only', '#7fb1ea', lambda c: B[(c, 0.65)]),
       ('λ 1, straightforward benefit only', '#2a78d6', lambda c: B[(c, 1.0)])]
fig, ax = plt.subplots(figsize=(10.5, 6.2))
fig.subplots_adjust(left=0.08, right=0.98, top=0.86, bottom=0.2)
x = np.arange(len(CAPS)); w = 0.26
for k, (lab, col, f) in enumerate(SER):
    vals = [f(c) for c, _ in CAPS]
    ax.bar(x + (k - 1) * w, vals, w * 0.92, color=col, label=lab, zorder=3)
    for xi, v in zip(x, vals):
        ax.text(xi + (k - 1) * w, v + 0.25, f"{v:.1f}", ha='center', va='bottom', fontsize=9.5, color=T1)
ax.set_xticks(x); ax.set_xticklabels([l for _, l in CAPS])
ax.set_xlabel('Infinite Coding Labor Asymptote'); ax.set_ylabel('Takeoff, AC → ASI (months)')
ax.set_ylim(0, 15.5); ax.grid(axis='y', color=GRID, lw=0.8); ax.set_axisbelow(True)
for s in ('top', 'right', 'left'): ax.spines[s].set_visible(False)
ax.tick_params(axis='x', length=0)
ax.legend(loc='lower left', bbox_to_anchor=(0, 1.02), ncol=3, frameon=False, fontsize=10)
fig.text(0.08, 0.035,
  "Straightforward benefit only: λ switched only where coding labor turns into progress after today; today's uplift, the fit to history, the η adjustment\n"
  "and the serial-labor cap stay at λ 0.5. The Time Horizon and Revenue anchors show the same pattern. AC: Automated Coder. ASI: Artificial Superintelligence.\n"
  "AI Futures Model (aifm-public, commit 1c40ecdb), Coding Uplift anchor, Daniel 08/16/26 preset, single runs at preset medians.",
  fontsize=7.8, color=MUTED, ha='left')
fig.savefig('lambda-asymptote-takeoff-bars.png', dpi=200)
