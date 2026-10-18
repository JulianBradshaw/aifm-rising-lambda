# Takeoff against the Infinite Coding Labor Asymptote with only λ's straightforward benefit switched on.
import json, csv, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
S, T1, T2, MUTED, GRID = '#fcfcfb', '#0b0b0b', '#52514e', '#8a8984', '#e6e5e0'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10.5,'axes.edgecolor':MUTED,
  'axes.labelcolor':T2,'xtick.color':T2,'ytick.color':T2,'figure.facecolor':S,'axes.facecolor':S})
R = json.load(open('asym_benefit_raw.json'))
w = csv.DictWriter(open('asym_benefit.csv', 'w', newline=''), fieldnames=['anchor_mode', 'asymptote', 'lambda_benefit_only', 'ac', 'asi', 'takeoff_months'])
w.writeheader()
for r in R: w.writerow(dict(anchor_mode=r['mode'], asymptote=r['asymptote'], lambda_benefit_only=r['lam'],
                            ac=round(r['ac'], 4), asi=round(r['asi'], 4), takeoff_months=round(r['takeoff_months'], 2)))
LAMS = [(0.5, 'λ 0.5', '#8a8984'), (0.65, 'λ 0.65 (benefit only)', '#7fb1ea'), (1.0, 'λ 1 (benefit only)', '#2a78d6')]
MODES = [('uplift-solved', 'Coding Uplift anchor'), ('time-horizon', 'Time Horizon anchor'), ('revenue', 'Revenue anchor')]
TICKS = [10, 100, 1e3, 1e4, 1e5, 1e8]; TL = ['10×', '100×', '10³×', '10⁴×', '10⁵×', '10⁸×']
fig, axes = plt.subplots(2, 3, figsize=(12.5, 8.2), sharex=True, sharey='row', gridspec_kw=dict(hspace=0.28, wspace=0.07))
fig.subplots_adjust(left=0.075, right=0.985, top=0.88, bottom=0.15)
for j, (mode, title) in enumerate(MODES):
    T = {(r['asymptote'], r['lam']): r['takeoff_months'] for r in R if r['mode'] == mode}
    caps = sorted({c for c, _ in T})
    a, b = axes[0, j], axes[1, j]
    for lam, lab, c in LAMS:
        a.plot(caps, [T[(x, lam)] for x in caps], color=c, lw=2.2, marker='o', ms=3.5, label=lab)
        if lam != 0.5:
            b.plot(caps, [100 * (1 - T[(x, lam)] / T[(x, 0.5)]) for x in caps], color=c, lw=2.2, marker='o', ms=3.5)
    for ax in (a, b):
        ax.set_xscale('log'); ax.axvline(15, color=T2, lw=0.9, ls=(0, (3, 2)))
        ax.grid(color=GRID, lw=0.8); ax.set_axisbelow(True)
        for s in ('top', 'right'): ax.spines[s].set_visible(False)
    a.set_title(title, fontsize=11, color=T1, loc='left')
    a.set_ylim(0, 23); b.set_ylim(0, 80)
    t05, t1 = T[(15, 0.5)], T[(15, 1.0)]
    a.annotate(f"15× default:\n{t05:.1f} → {t1:.1f} mo", xy=(15, t1), xytext=(40, 15.5), fontsize=9, color=T1,
               arrowprops=dict(arrowstyle='-', color=MUTED, lw=0.8))
    u05, u1 = T[(1e8, 0.5)], T[(1e8, 1.0)]
    a.annotate(f"Unbounded:\n{u05:.1f} → {u1:.1f} mo", xy=(1e8, u05), xytext=(2e4, 11), fontsize=9, color=T1, ha='center',
               arrowprops=dict(arrowstyle='-', color=MUTED, lw=0.8))
    b.set_xticks(TICKS); b.set_xticklabels(TL, fontsize=9.5); b.minorticks_off()
    b.set_xlabel('Infinite Coding Labor Asymptote')
axes[0, 0].set_ylabel('Takeoff, AC → ASI (months)')
axes[1, 0].set_ylabel('Takeoff shortened vs λ 0.5 (%)')
axes[0, 0].legend(loc='lower left', bbox_to_anchor=(0, 1.13), ncol=3, frameon=False, fontsize=10.5)
fig.text(0.075, 0.035,
  "Benefit only: λ switched only where coding labor turns into progress after today. Today's uplift, the fit to history, the η adjustment and the serial-labor cap\n"
  "stay at λ 0.5, with labor levels pinned at today's values. Dashed line: the default 15×. AC: Automated Coder. ASI: Artificial Superintelligence.\n"
  "AI Futures Model (aifm-public, commit 1c40ecdb), Daniel 08/16/26 preset, single runs at preset medians.",
  fontsize=7.8, color=MUTED, ha='left')
fig.savefig('lambda-benefit-vs-asymptote.png', dpi=200)
