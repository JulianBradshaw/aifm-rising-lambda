# Where the after-today λ 0.5 → 0.65 labor gain goes, averaged over every order of switching the uses (as in the per-use chart).
import csv, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
S, T1, T2, MUTED, GRID, NEUT = '#fcfcfb', '#0b0b0b', '#52514e', '#8a8984', '#e6e5e0', '#6f6e69'
GAIN, DRAG = '#2a78d6', '#e34948'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10.5,'axes.edgecolor':MUTED,
  'axes.labelcolor':T2,'xtick.color':T2,'ytick.color':T2,'figure.facecolor':S,'axes.facecolor':S})
rows = {r['anchor_mode']: r for r in csv.DictReader(open('benefit_drag_avg.csv'))}
PANELS = [('uplift-solved', 'Coding Uplift anchor'), ('time-horizon', 'Time Horizon anchor'), ('revenue', 'Revenue anchor')]
fig, axes = plt.subplots(3, 1, figsize=(10, 13.5), sharex=True, gridspec_kw=dict(hspace=0.38))
fig.subplots_adjust(left=0.335, right=0.87, top=0.95, bottom=0.12)
for ax, (mode, title) in zip(axes, PANELS):
    r = rows[mode]; v = lambda k: float(r[k])
    drags = [("CES bottleneck", v('share_lost_ces')),
             ("Infinite Coding Labor Asymptote (15×)", v('share_lost_asymptote')),
             ("Research-stock lag and\ntraining compute share", v('share_lost_stock_training')),
             ("Backloading\n(most labor growth arrives just before AC)", v('share_lost_backloading'))]
    items = [(f"λ gain on serial coding labor at AC\n({v('serial_labor_gain_at_ac'):.1f}× more serial labor)", 0, 100, GAIN)]
    left = 100
    for lab, d in drags:
        left -= d; items.append((lab, left, d, DRAG))
    items.append((f"Left to speed up AC\n({abs(v('ac_shift_months_shapley')):.1f} months saved)", 0, v('share_left'), NEUT))
    for i, (lab, x0, w, col) in enumerate(items):
        ax.barh(i, w, left=x0, height=0.56, color=col, zorder=3)
        last = i == len(items)-1
        txt = f"{w:.0f}%" if i == 0 or last else f"−{w:.0f}%"
        ax.text(1.02, i, txt, transform=ax.get_yaxis_transform(), va='center', ha='left', fontsize=10, color=T1, fontweight='bold' if last else 'normal')
        if not last:
            ax.plot([x0, x0] if i else [100, 100], [i+0.28, i+0.72], color=MUTED, lw=0.8, ls=(0,(2,2)), zorder=2)
    ax.set_yticks(range(len(items))); ax.set_yticklabels([it[0] for it in items]); ax.set_ylim(len(items)-0.4, -0.6)
    ax.set_title(title, fontsize=11, color=T1, loc='left')
    ax.axvline(0, color=T2, lw=1, zorder=2); ax.set_xlim(0, 105)
    ax.grid(axis='x', color=GRID, lw=0.8); ax.set_axisbelow(True)
    for s in ('top','right','left'): ax.spines[s].set_visible(False)
    ax.tick_params(axis='y', length=0); ax.tick_params(axis='x', labelbottom=True)
axes[-1].set_xlabel('Share of the λ 0.65 labor gain, in log terms (%)')
fig.text(0.02, 0.02,
  "The after-today use of λ (the \"straightforward coding labor benefit\" of the per-use chart) switched from 0.5 to 0.65, averaged over every order of switching\n"
  "the uses, so months saved match that chart. Shares are in log terms so the drags add up. Bottleneck drags: experiment capacity at AC with the extra serial\n"
  "labor, everything else equal; the asymptote's share is how much less is lost when the 15× is raised to 10,000 (which also flattens the CES curve).\n"
  "Research-stock lag and training compute: progress rate vs experiment capacity at AC. Backloading: average extra progress from today to AC vs the rate at AC.\n"
  "AI Futures Model (aifm-public, commit 1c40ecdb), Daniel 08/16/26 preset, single runs at preset medians.",
  fontsize=7.8, color=MUTED, ha='left')
fig.savefig('lambda-benefit-drag.png', dpi=200)
