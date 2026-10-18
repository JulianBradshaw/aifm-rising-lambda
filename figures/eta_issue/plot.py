# Figure for the η-adjustment issue: power vs linear rescaling of η across λ.
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
S, T1, T2, MUTED, GRID = '#fcfcfb', '#0b0b0b', '#52514e', '#8a8984', '#e6e5e0'
PW, LI = '#eb6834', '#2a78d6'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10.5,'axes.edgecolor':MUTED,
  'axes.labelcolor':T2,'xtick.color':T2,'ytick.color':T2,'figure.facecolor':S,'axes.facecolor':S})
lam = np.linspace(0.1, 1.0, 400)
fig, (a, b) = plt.subplots(1, 2, figsize=(11, 5))
fig.subplots_adjust(left=0.07, right=0.98, top=0.88, bottom=0.2, wspace=0.25)
for ax in (a, b):
    ax.axvline(0.5, color=MUTED, lw=1, ls=(0, (2, 3)))
    ax.set_xlim(0.1, 1.0); ax.set_xlabel('λ (coding labor parallelization penalty)')
    ax.grid(axis='y', color=GRID, lw=0.8); ax.set_axisbelow(True)
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
# Panel A: default η = 3
a.plot(lam, 3 ** (0.5 / lam), color=PW, lw=2.2, label='current: η^(0.5/λ)')
a.plot(lam, 3 * 0.5 / lam, color=LI, lw=2.2, label='proposed: η·(0.5/λ)')
a.set_yscale('log'); a.set_ylim(1, 400)
a.set_yticks([1, 2, 3, 5, 10, 20, 50, 100, 200]); a.set_yticklabels(['1', '2', '3', '5', '10', '20', '50', '100', '200'])
a.set_ylabel('adjusted η (OOMs per progress-year)')
a.set_title('Default η = 3', loc='left', color=T1, fontsize=11)
for l in (0.1, 0.2, 0.3, 1.0):
    p, q = 3 ** (0.5 / l), 1.5 / l
    box = dict(boxstyle='square,pad=0.15', fc=S, ec='none')
    # Both curves fall to the right: orange labels go above-right, blue labels below-left, clear of the lines
    a.annotate(f'{p:,.3g}', (l, p), xytext=(6 if l < 1 else -4, 6), textcoords='offset points', ha='left' if l < 1 else 'right', va='bottom', fontsize=8.5, color=T1, bbox=box, zorder=5)
    if l > 0.1:
        a.annotate(f'{q:,.3g}', (l, q), xytext=(-6, -8), textcoords='offset points', ha='right', va='top', fontsize=8.5, color=T1, bbox=box, zorder=5)
    else:  # at the left edge there is no room below-left; above-right is clear of the falling line
        a.annotate(f'{q:,.3g}', (l, q), xytext=(7, 4), textcoords='offset points', ha='left', va='bottom', fontsize=8.5, color=T1, bbox=box, zorder=5)
    a.plot([l], [p], marker='o', ms=4, color=PW, zorder=4); a.plot([l], [q], marker='o', ms=4, color=LI, zorder=4)
a.legend(frameon=False, loc='upper right', labelcolor=T1)
# Panel B: the ratio adjusted/input for several η: the power form depends on η's value, the linear one doesn't
for eta, ls in [(0.5, (0, (1, 2))), (1.0, (0, (5, 3))), (3.0, '-'), (9.0, (0, (8, 2, 1, 2)))]:
    b.plot(lam, eta ** (0.5 / lam) / eta, color=PW, lw=1.8, ls=ls, label=f'current, η = {eta:g}')
b.plot(lam, 0.5 / lam, color=LI, lw=2.6, label='proposed, any η')
b.axhline(1, color=MUTED, lw=0.8)
b.set_yscale('log'); b.set_ylim(0.2, 20)
b.set_yticks([0.25, 0.5, 1, 2, 5, 10]); b.set_yticklabels(['0.25×', '0.5×', '1×', '2×', '5×', '10×'])
b.set_ylabel('adjusted η ÷ input η')
b.set_title('Scaling applied, by input η', loc='left', color=T1, fontsize=11)
b.legend(frameon=False, loc='upper right', labelcolor=T1, fontsize=9)
fig.text(0.07, 0.04, 'Both forms agree at λ = 0.5. The current form scales η by an amount that depends on η itself: it does nothing at η = 1 and\n'
         'moves η the wrong way for η < 1 (10% of the lognormal [1, 9] prior). Rescaling a quantity measured in OOMs should not depend on its value.',
         fontsize=8.5, color=MUTED, ha='left')
fig.savefig('eta-adjustment-issue.png', dpi=170)
