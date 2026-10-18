# The model's β (ideas getting harder to find; its r_software is 1/β) after the historical calibration at λ 0.5 / 0.65 / 1, and the
# takeoff with that refit's contribution (its Shapley value, as in the lambda-uses-takeoff waterfalls). Data: attrib_raw.json, lambda_uses_takeoff.csv.
import json, csv, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
S, T1, T2, MUTED, GRID = '#fcfcfb', '#0b0b0b', '#52514e', '#8a8984', '#e6e5e0'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.edgecolor':MUTED,
  'axes.labelcolor':T2,'xtick.color':T2,'ytick.color':T2,'figure.facecolor':S,'axes.facecolor':S})
R = [r for r in json.load(open('attrib_raw.json')) if r['asymptote'] == '15' and r['mode'] == 'uplift-solved']
base = next(r for r in R if r['subset'] == [] and r['target'] == 1.0)
hist = {r['target']: r for r in R if r['subset'] == ['history']}
rows = [(0.5, base), (0.65, hist[0.65]), (1.0, hist[1.0])]
SH = {float(r['lambda_to']): float(r['months_shapley']) for r in csv.DictReader(open('lambda_uses_takeoff.csv'))
      if r['asymptote'] == '15' and r['anchor_mode'] == 'uplift-solved' and r['measure'] == 'takeoff' and r['use'] == 'history'}
T0 = 12 * (base['asi'] - base['ac'])
takeoff = lambda lam: T0 + SH.get(lam, 0.0)
COL = {0.5: '#8a8984', 0.65: '#7fb1ea', 1.0: '#2a78d6'}
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.5, 5.2), gridspec_kw=dict(wspace=0.3))
fig.subplots_adjust(left=0.08, right=0.98, top=0.86, bottom=0.27)
for ax, key, ylab, top, fmt in [(a1, lambda lam, r: 1 / r['r_sw'], 'β, diminishing returns to software research', 0.42, '{:.3f}'),
                                (a2, lambda lam, r: takeoff(lam), 'Takeoff, AC → ASI (months)', 20.5, '{:.1f} mo')]:
    v0 = key(*rows[0])
    for i, (lam, r) in enumerate(rows):
        v = key(lam, r)
        ax.bar(i, v, 0.6, color=COL[lam], zorder=3)
        lab = fmt.format(v) + ('' if i == 0 else f"\n({100 * (v / v0 - 1):+.0f}%)")
        ax.text(i, v + top * 0.015, lab, ha='center', va='bottom', fontsize=10.5, color=T1)
    ax.set_xticks(range(3)); ax.set_xticklabels([f"λ {l:g}" for l, _ in rows])
    ax.set_ylabel(ylab); ax.set_ylim(0, top)
    ax.grid(axis='y', color=GRID, lw=0.8); ax.set_axisbelow(True); ax.tick_params(axis='x', length=0)
    for s in ('top', 'right', 'left'): ax.spines[s].set_visible(False)
a1.set_title('β after calibrating to 2024', fontsize=11, color=T1, loc='left')
a2.set_title('Takeoff length after β calibration', fontsize=11, color=T1, loc='left')
fig.text(0.08, 0.035,
  "β: how many 10×s of cumulative research it takes for 10× software efficiency (the model's Returns to Software Research Effort; higher β means ideas\n"
  "get harder to find faster). The model sets β so that software efficiency grows 1.0 OOM/yr in 2024; at higher λ, past human labor growth counts for more,\n"
  "so β comes out higher. β is the same under every AC anchor. Right: λ 0.5 takeoff plus this refit's average contribution over every switching order,\n"
  "as in the takeoff waterfalls; Coding Uplift anchor. AC: Automated Coder. ASI: Artificial Superintelligence.\n"
  "AI Futures Model (aifm-public, commit 1c40ecdb), Daniel 08/16/26 preset, single runs at preset medians.",
  fontsize=7.8, color=MUTED, ha='left')
fig.savefig('lambda-beta-software.png', dpi=200)
