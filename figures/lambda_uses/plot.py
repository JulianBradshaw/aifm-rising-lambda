# Waterfall of the AC shift from λ 0.5 to λ_to, split by use of λ, one panel per AC anchor. Usage: python plot.py 1.0
import csv, sys, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
TO = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
S, T1, T2, MUTED, GRID, NEUT = '#fcfcfb', '#0b0b0b', '#52514e', '#8a8984', '#e6e5e0', '#6f6e69'
LATER, EARLIER = '#e34948', '#2a78d6'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10.5,'axes.edgecolor':MUTED,
  'axes.labelcolor':T2,'xtick.color':T2,'ytick.color':T2,'figure.facecolor':S,'axes.facecolor':S})
rows = [r for r in csv.DictReader(open('lambda_uses_ac.csv')) if float(r['lambda_to']) == TO]
MON = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
def ym(y):
    yr = int(y); m = int((y-yr)*12)
    return f"{MON[m]} {yr}"
USES = [('anchor', "Serial coding uplift\nbackcalculation effects"),
        ('dynamics', "Straightforward coding labor benefit\nof higher λ, after today"),
        ('history', "Calibrating coding labor benefit\nof higher λ, before today"),
        ('eta', "Rescaling AI labor-per-GPU growth (η)"),
        ('cap', "Converting the Maximum Serial\nCoding Labor Multiplier (1e8)")]
PANELS = [('uplift-solved', 'Coding Uplift anchor'), ('time-horizon', 'Time Horizon anchor'), ('revenue', 'Revenue anchor')]
fig, axes = plt.subplots(3, 1, figsize=(10, 13), sharex=True, gridspec_kw=dict(hspace=0.32))
fig.subplots_adjust(left=0.33, right=0.88, top=0.95, bottom=0.11)
for ax, (mode, title) in zip(axes, PANELS):
    d = {r['use']: r for r in rows if r['anchor_mode'] == mode}
    r0 = next(iter(d.values())); base, full, tot = float(r0['ac_lambda05']), float(r0['ac_lambda_to']), float(r0['total_months'])
    cum = 0.0; n = len(USES)
    for i, (u, _) in enumerate(USES):
        y = i; v = float(d[u]['months_shapley']); lo, hi = sorted([float(d[u]['months_alone']), float(d[u]['months_last'])])
        if abs(v) >= 0.05:
            ax.barh(y, v, left=cum, height=0.56, color=LATER if v > 0 else EARLIER, zorder=3)
        else:
            ax.plot([cum], [y], marker='|', ms=12, color=MUTED, zorder=3)
        if abs(hi - lo) >= 0.15:
            ax.plot([cum+lo, cum+hi], [y+0.38, y+0.38], color=T2, lw=1.1, zorder=4)
            for x in (cum+lo, cum+hi): ax.plot([x, x], [y+0.31, y+0.45], color=T2, lw=1.1, zorder=4)
        ax.text(1.02, y, f"{v:+.1f} mo" if abs(v) >= 0.05 else "≈0", transform=ax.get_yaxis_transform(),
                va='center', ha='left', fontsize=10, color=T1)
        if i < n - 1:
            ax.plot([cum+v, cum+v], [y+0.28, y+0.72], color=MUTED, lw=0.8, ls=(0,(2,2)), zorder=2)
        cum += v
    ax.plot([cum, cum], [n-1+0.28, n-0.28], color=MUTED, lw=0.8, ls=(0,(2,2)), zorder=2)
    ax.barh(n, tot, height=0.56, color=NEUT, zorder=3)
    ax.text(1.02, n, f"{tot:+.1f} mo", transform=ax.get_yaxis_transform(), va='center', ha='left', fontsize=10, color=T1, fontweight='bold')
    ax.axvline(0, color=T2, lw=1, zorder=2)
    ax.set_title(f"{title}: AC {ym(base)} at λ 0.5 → {ym(full)} at λ {TO:g}", fontsize=11, color=T1, loc='left')
    ax.grid(axis='x', color=GRID, lw=0.8); ax.set_axisbelow(True)
    for s in ('top','right','left'): ax.spines[s].set_visible(False)
    ax.tick_params(axis='y', length=0); ax.tick_params(axis='x', labelbottom=True)
    ax.set_yticks(range(n+1)); ax.set_yticklabels([l for _, l in USES] + [f"Net effect for λ = {TO:g}"])
    ax.set_ylim(n+0.6, -0.6)
lo_x = min(a.get_xlim()[0] for a in axes); hi_x = max(a.get_xlim()[1] for a in axes)
for ax in axes: ax.set_xlim(lo_x - 0.5, hi_x + 0.5)
axes[-1].set_xlabel('Change in AC date (months; later →)')
fig.text(0.02, 0.02,
  "Bars: the average contribution of each use of λ, over every order of switching the uses from λ 0.5 to the new λ (they sum\n"
  "to the net). Whiskers: the effect if that use is switched first vs last. Three other uses have no effect on AC: normalizing the Infinite\n"
  "Coding Labor Asymptote to today's labor (cancels once labor levels are pinned at today), the AI2027-SC target and the output metrics.\n"
  "AI Futures Model (aifm-public, commit 1c40ecdb), Daniel 08/16/26 preset, single runs at preset medians.\n"
  "λ switched use by use with labor levels pinned at today's values.",
  fontsize=7.8, color=MUTED, ha='left')
fig.savefig(f"lambda-uses-ac-{TO:g}.png", dpi=200)
