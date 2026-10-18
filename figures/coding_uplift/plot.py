import csv, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
S, T1, T2, MUTED, GRID = '#fcfcfb', '#0b0b0b', '#52514e', '#8a8984', '#e6e5e0'
C1 = '#2a78d6'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.edgecolor':MUTED,
  'axes.labelcolor':T2,'xtick.color':T2,'ytick.color':T2,'figure.facecolor':S,'axes.facecolor':S})
rows = list(csv.DictReader(open('coding_uplift_curves.csv')))
PD = 2026.578
MON = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
def ylab(y):
    yr = int(y); m = round((y-yr)*12)
    if m == 12: yr, m = yr+1, 0
    return f"{MON[m]} {yr}"
def curve(up):
    r = [x for x in rows if float(x['uplift']) == up]
    return [float(x['year']) for x in r], [100*float(x['automated_fraction']) for x in r], float(r[0]['ac_year'])
def at(x, y, t):
    import numpy as np; return float(np.interp(t, x, y))

fig = plt.figure(figsize=(9, 7.2))
# --- flow strip ---
fx = fig.add_axes([0.04, 0.80, 0.92, 0.17]); fx.set_xlim(0, 100); fx.set_ylim(0, 20); fx.axis('off')
boxes = [(1, 'Input', 'Serial coding uplift\nis 2× in Aug 2026'),
         (35, 'Back-calculated', 'Share of coding tasks\nautomated today: ~60%'),
         (69, 'Extrapolated', 'AC = date the share\nreaches 100%: Oct 2027')]
for x0, head, body in boxes:
    fx.add_patch(FancyBboxPatch((x0, 1.5), 30, 15, boxstyle='round,pad=0.4,rounding_size=1.5',
                 fc='#eef4fc' if x0 == 1 else S, ec=C1 if x0 == 1 else MUTED, lw=1.2))
    fx.text(x0+15, 13.6, head, ha='center', va='center', fontsize=9, color=T2)
    fx.text(x0+15, 7.2, body, ha='center', va='center', fontsize=10.5, color=T1, linespacing=1.4)
for x0 in (31.6, 65.6):
    fx.annotate('', xy=(x0+3, 9), xytext=(x0, 9), arrowprops=dict(arrowstyle='-|>', color=T2, lw=1.4))

# --- annotated curve ---
ax = fig.add_axes([0.09, 0.15, 0.80, 0.58])
styles = {1.5: dict(lw=1.5, alpha=0.55, ls=(0,(4,2))), 2.0: dict(lw=2.4, alpha=1.0, ls='-'), 3.0: dict(lw=1.5, alpha=0.55, ls=(0,(1,1.6)))}
for up in (1.5, 2.0, 3.0):
    x, y, ac = curve(up); st = styles[up]
    ax.plot(x, y, color=C1, lw=st['lw'], alpha=st['alpha'], ls=st['ls'], zorder=3)
    fn = at(x, y, PD)
    ax.plot([PD], [fn], 'o', color=C1, ms=6, alpha=st['alpha'], zorder=4)
    ax.plot([ac], [100], 'o', color=T1 if up == 2.0 else MUTED, ms=5, zorder=4)
    lab = f"{up:g}× in Aug 2026" + (" (default)" if up == 2.0 else "")
    off, ha, va = {1.5: ((10, -8), 'left', 'top'), 2.0: ((-10, -4), 'right', 'center'), 3.0: ((-10, 2), 'right', 'center')}[up]
    ax.annotate(f"{lab}\n{fn:.0f}% automated today", (PD, fn), xytext=off, textcoords='offset points',
                ha=ha, va=va, fontsize=9.5, color=T1 if up == 2.0 else T2, zorder=5,
                bbox=dict(fc=S, ec='none', pad=1.5) if up != 1.5 else None)
    ax.annotate(f"AC {ylab(ac)}\n{(ac-PD)*12:.0f} months away", (ac, 100), xytext=(0, 38 if up == 2.0 else 8), textcoords='offset points',
                ha='center', va='bottom', fontsize=9, color=T1 if up == 2.0 else T2,
                arrowprops=dict(arrowstyle='-', color=MUTED, lw=0.8, shrinkA=2, shrinkB=4) if up == 2.0 else None)
ax.axhline(100, color=T2, lw=1, zorder=2)
ax.text(2025.02, 101.5, '100% automated = Automated Coder (AC)', fontsize=9, color=T2, va='bottom')
ax.axvline(PD, color=MUTED, lw=1, ls=(0,(2,3)), zorder=1)
ax.text(PD+0.02, 3, 'Aug 2026', fontsize=9, color=T2)
ax.set_xlim(2025.0, 2028.6); ax.set_ylim(0, 124)
xt = [2025.0, 2025.5, 2026.0, 2026.5, 2027.0, 2027.5, 2028.0, 2028.5]
ax.set_xticks(xt); ax.set_xticklabels([ylab(v) for v in xt])
ax.set_yticks([0, 20, 40, 60, 80, 100]); ax.set_yticklabels([f"{v}%" for v in [0,20,40,60,80,100]])
ax.set_ylabel('Share of coding tasks automated')
ax.grid(axis='y', color=GRID, lw=0.8); ax.set_axisbelow(True)
for s in ('top','right'): ax.spines[s].set_visible(False)
fig.text(0.04, 0.03, "Coding-uplift anchor. Each curve is fitted so the serial uplift on Aug 2026 equals the stated value and its excess over 1× doubles every 5 months.\n"
         "AI Futures Model (aifm-public, commit 1c40ecdb), Daniel 08/16/26 preset (λ 0.5), single runs at the preset's median parameters; only the Aug 2026 uplift varied.",
         fontsize=7.6, color=MUTED, ha='left')
fig.savefig('coding-uplift-to-ac.png', dpi=200)
