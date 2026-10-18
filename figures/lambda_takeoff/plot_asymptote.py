# Takeoff length at λ 0.5 vs λ 1, and the ASI date shift, at three settings of the
# Infinite Coding Labor Asymptote, for each AC anchor (Daniel 08/16/26).
import csv, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
S, T1, T2, MUTED, GRID = '#fcfcfb', '#0b0b0b', '#52514e', '#8a8984', '#e6e5e0'
C05, C1, LATER, EARLIER = '#8a8984', '#2a78d6', '#e34948', '#2a78d6'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10.5,'axes.edgecolor':MUTED,
  'axes.labelcolor':T2,'xtick.color':T2,'ytick.color':T2,'figure.facecolor':S,'axes.facecolor':S})
R = [r for r in csv.DictReader(open('lambda_uses_takeoff.csv')) if r['lambda_to'] == '1.0' and r['use'] == 'anchor']
get = lambda cap, mode, meas: next(r for r in R if r['asymptote'] == cap and r['anchor_mode'] == mode and r['measure'] == meas)
CAPS = [('15', '15× (default)'), ('100', '100×'), ('1e8', 'Effectively unbounded (1e8×)')]
MODES = [('uplift-solved', 'Coding Uplift anchor'), ('time-horizon', 'Time Horizon anchor'), ('revenue', 'Revenue anchor')]
rows = []
for mode, mt in MODES:
    for cap, ct in CAPS: rows.append((mode, mt, cap, ct))
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 7.2), sharey=True, gridspec_kw=dict(width_ratios=[1.35, 1], wspace=0.08))
fig.subplots_adjust(left=0.25, right=0.97, top=0.9, bottom=0.17)
ys = []; y = 0; labels = []
for i, (mode, mt, cap, ct) in enumerate(rows):
    if i and cap == '15': y += 0.8
    ys.append(y); labels.append(ct); y += 1
for yy, (mode, mt, cap, ct) in zip(ys, rows):
    t = get(cap, mode, 'takeoff'); x0, x1 = 12 * float(t['value_lambda05']), 12 * float(t['value_lambda_to'])
    a1.annotate('', xy=(x1, yy), xytext=(x0, yy), arrowprops=dict(arrowstyle='-|>', color=LATER if x1 > x0 else EARLIER, lw=1.6, shrinkA=4, shrinkB=4))
    a1.plot([x0], [yy], 'o', color=C05, ms=7, zorder=3); a1.plot([x1], [yy], 'o', color=C1, ms=7, zorder=3)
    a1.text(max(x0, x1) + 0.6, yy, f"{x0:.1f} → {x1:.1f} mo", va='center', fontsize=9.5, color=T1)
    d = float(get(cap, mode, 'asi')['total_months'])
    a2.barh(yy, d, height=0.55, color=LATER if d > 0 else EARLIER, zorder=3)
    a2.text(d + (0.3 if d >= 0 else -0.3), yy, f"{d:+.1f} mo", va='center', ha='left' if d >= 0 else 'right', fontsize=9.5, color=T1)
for k, (mode, mt) in enumerate(MODES):
    a1.text(-0.02, ys[3 * k] - 0.75, mt, transform=a1.get_yaxis_transform(), ha='right', fontsize=10.5, color=T1, fontweight='bold')
a1.set_yticks(ys); a1.set_yticklabels(labels); a1.set_ylim(max(ys) + 0.7, -1.2)
a1.set_xlim(0, 27); a1.set_xlabel('Takeoff length, AC → ASI (months)')
a2.set_xlim(-8, 17); a2.axvline(0, color=T2, lw=1, zorder=2); a2.set_xlabel('Change in ASI date, λ 0.5 → 1 (months; later →)')
for a in (a1, a2):
    a.grid(axis='x', color=GRID, lw=0.8); a.set_axisbelow(True); a.tick_params(axis='y', length=0)
    for s in ('top', 'right', 'left'): a.spines[s].set_visible(False)
a1.plot([], [], 'o', color=C05, label='λ 0.5'); a1.plot([], [], 'o', color=C1, label='λ 1')
a1.legend(loc='upper right', frameon=False, ncol=2, bbox_to_anchor=(1.0, 1.08))
a1.text(0, 1.04, 'Infinite Coding Labor Asymptote', transform=a1.transAxes, fontsize=10, color=T2, ha='left')
fig.text(0.02, 0.03,
  "AC: Automated Coder. ASI: Artificial Superintelligence. The Infinite Coding Labor Asymptote is how much faster AI research could go with\n"
  "unlimited coding labor and today's experiment compute. AI Futures Model (aifm-public, commit 1c40ecdb), Daniel 08/16/26 preset, single runs\n"
  "at preset medians, only λ and the asymptote varied.", fontsize=7.8, color=MUTED, ha='left')
fig.savefig('lambda-takeoff-asymptote.png', dpi=200)
