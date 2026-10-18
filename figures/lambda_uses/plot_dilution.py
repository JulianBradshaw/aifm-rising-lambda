# How the after-today λ 0.5 → 0.65 labor gain shrinks on the way to AC, one panel per AC anchor.
import csv, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
S, T1, T2, MUTED, GRID = '#fcfcfb', '#0b0b0b', '#52514e', '#8a8984', '#e6e5e0'
C1 = '#2a78d6'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10.5,'axes.edgecolor':MUTED,
  'axes.labelcolor':T2,'xtick.color':T2,'ytick.color':T2,'figure.facecolor':S,'axes.facecolor':S})
rows = {r['anchor_mode']: r for r in csv.DictReader(open('benefit_dilution.csv'))}
PANELS = [('uplift-solved', 'Coding Uplift anchor'), ('time-horizon', 'Time Horizon anchor'), ('revenue', 'Revenue anchor')]
fig, axes = plt.subplots(3, 1, figsize=(10, 11.5), sharex=True, gridspec_kw=dict(hspace=0.38))
fig.subplots_adjust(left=0.33, right=0.88, top=0.95, bottom=0.12)
for ax, (mode, title) in zip(axes, PANELS):
    r = rows[mode]; G = float(r['labor_growth_to_ac'])
    steps = [(f"Serial coding labor at AC\n({G:,.0f}× labor growth, ^0.15)", float(r['serial_labor_gain_at_ac'])),
             ("Experiment throughput at AC\n(compute bottleneck)", float(r['throughput_gain_at_ac'])),
             ("Progress rate at AC\n(research-stock lag, training compute)", float(r['progress_rate_gain_at_ac'])),
             ("Average extra progress, today → AC\n(gain is back-loaded)", 1 + float(r['avg_extra_progress']))]
    for i, (lab, v) in enumerate(steps):
        g = 100*(v-1)
        ax.barh(i, g, height=0.56, color=C1, zorder=3)
        ax.text(1.02, i, f"+{g:.0f}%" if g >= 10 else f"+{g:.1f}%", transform=ax.get_yaxis_transform(), va='center', ha='left', fontsize=10, color=T1)
    ax.set_yticks(range(len(steps))); ax.set_yticklabels([l for l, _ in steps]); ax.set_ylim(len(steps)-0.4, -0.6)
    ax.set_title(f"{title}: AC {abs(float(r['ac_shift_months'])):.1f} months earlier, out of {float(r['months_today_to_ac']):.1f} months to AC",
                 fontsize=11, color=T1, loc='left')
    ax.axvline(0, color=T2, lw=1, zorder=2)
    ax.grid(axis='x', color=GRID, lw=0.8); ax.set_axisbelow(True)
    for s in ('top','right','left'): ax.spines[s].set_visible(False)
    ax.tick_params(axis='y', length=0); ax.tick_params(axis='x', labelbottom=True)
axes[-1].set_xlabel('Gain from λ 0.65 vs λ 0.5, applied to coding labor growth after today (%)')
fig.text(0.02, 0.02,
  "Only the after-today use of λ is switched (the \"straightforward coding labor benefit\" row of the per-use chart); today's levels and the automation schedule\n"
  "are held at λ 0.5. Throughput gain: experiment capacity at AC with the extra serial labor, everything else equal. Progress-rate gain: ratio of the two\n"
  "runs' progress rates at the λ 0.5 AC date. Average extra progress: additional progress made by that date, over the progress the λ 0.5 run makes.\n"
  "AI Futures Model (aifm-public, commit 1c40ecdb), Daniel 08/16/26 preset, single runs at preset medians.",
  fontsize=7.8, color=MUTED, ha='left')
fig.savefig('lambda-benefit-dilution.png', dpi=200)
