# Takeoff length vs λ under three ways of adjusting η for λ, one panel per AC anchor.
import json, csv, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
S, T1, T2, MUTED, GRID = '#fcfcfb', '#0b0b0b', '#52514e', '#8a8984', '#e6e5e0'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10.5,'axes.edgecolor':MUTED,
  'axes.labelcolor':T2,'xtick.color':T2,'ytick.color':T2,'figure.facecolor':S,'axes.facecolor':S})
R = json.load(open('eta_sweep_raw.json'))
w = csv.DictWriter(open('eta_sweep.csv', 'w', newline=''), fieldnames=['anchor_mode', 'eta_form', 'lambda', 'eta_used', 'ac', 'asi', 'takeoff_months'])
w.writeheader()
for r in R: w.writerow(dict(anchor_mode=r['mode'], eta_form=r['form'], **{'lambda': r['lam']}, eta_used=round(r['eta_used'], 4),
                            ac=round(r['ac'], 4), asi=round(r['asi'], 4), takeoff_months=round(r['takeoff_months'], 2)))
FORMS = [('power', "η^(0.5/λ), the model's adjustment", '#2a78d6', '-'),
         ('linear', 'η·(0.5/λ), linear in OOMs', '#e34948', '-'),
         ('none', 'No adjustment (η = 3 at every λ)', '#8a8984', '--')]
MODES = [('uplift-solved', 'Coding Uplift anchor'), ('time-horizon', 'Time Horizon anchor'), ('revenue', 'Revenue anchor')]
fig, axes = plt.subplots(1, 3, figsize=(12, 4.6), sharey=True, gridspec_kw=dict(wspace=0.08))
fig.subplots_adjust(left=0.07, right=0.98, top=0.82, bottom=0.25)
for ax, (mode, title) in zip(axes, MODES):
    for f, lab, c, ls in FORMS:
        pts = sorted((r['lam'], r['takeoff_months']) for r in R if r['mode'] == mode and r['form'] == f)
        ax.plot([p[0] for p in pts], [p[1] for p in pts], color=c, ls=ls, lw=2, label=lab)
    ax.axvline(0.5, color=MUTED, lw=0.8, ls=(0, (2, 2)))
    ax.set_title(title, fontsize=11, color=T1, loc='left'); ax.set_xlabel('λ')
    ax.grid(color=GRID, lw=0.8); ax.set_axisbelow(True)
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
axes[0].set_ylabel('Takeoff, AC → ASI (months)')
axes[0].legend(loc='lower left', bbox_to_anchor=(0, 1.1), ncol=3, frameon=False, fontsize=10)
fig.text(0.01, 0.03,
  "η: Coding Automation Efficiency Improvement Factor, 3 OOMs at λ 0.5 in Daniel's preset. AC: Automated Coder. ASI: Artificial Superintelligence.\n"
  "AI Futures Model (aifm-public, commit 1c40ecdb), Daniel 08/16/26 preset, single runs at preset medians, only λ and the η adjustment varied.",
  fontsize=7.8, color=MUTED, ha='left')
fig.savefig('lambda-eta-adjustment.png', dpi=200)
