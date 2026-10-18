# The model's η adjustment, η^(0.5/λ), against the proposed linear η·(0.5/λ), for η = 3 (the model's default).
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
S, T1, T2, MUTED, GRID = '#fcfcfb', '#0b0b0b', '#52514e', '#8a8984', '#e6e5e0'
C = {'power':'#eb6834', 'linear':'#2a78d6'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.edgecolor':MUTED,
  'axes.labelcolor':T2,'xtick.color':T2,'ytick.color':T2,'figure.facecolor':S,'axes.facecolor':S})
ETA = 3.0
lam = np.linspace(0.1, 1.0, 400)
pw, li = ETA ** (0.5 / lam), ETA * 0.5 / lam
fig, a1 = plt.subplots(figsize=(8, 6))
fig.subplots_adjust(left=0.1, right=0.97, top=0.96, bottom=0.19)
for ax in (a1,):
    for gx, lab in [(0.5, 'λ 0.5\nAI Futures\nModel default'), (0.65, 'λ 0.65\nfork\nestimated')]:
        ax.axvline(gx, color=MUTED, lw=1, ls=(0,(2,3)), zorder=1)
    ax.set_xlim(0.1, 1.0); ax.set_xticks([0.1,0.2,0.3,0.4,0.5,0.6,0.65,0.7,0.8,0.9,1.0]); ax.set_xticklabels(['0.1','0.2','0.3','0.4','0.5','0.6','0.65','0.7','0.8','0.9','1.0'])
    ax.set_xlabel('λ', fontsize=13); ax.grid(axis='y', color=GRID, lw=0.8, which='major'); ax.set_axisbelow(True)
    for s in ('top','right'): ax.spines[s].set_visible(False)
a1.plot(lam, pw, color=C['power'], lw=2.2, label="Model, η^(0.5/λ)")
a1.plot(lam, li, color=C['linear'], lw=2.2, label="Corrected model, η·(0.5/λ)")
a1.set_yscale('log'); a1.set_ylim(1, 400)
a1.set_yticks([1, 2, 3, 5, 10, 20, 50, 100, 200]); a1.set_yticklabels(['1','2','3','5','10','20','50','100','200'])
a1.set_ylabel('Effective η (log scale)', fontsize=10.5)
for l in (0.1, 0.2, 0.3, 0.65, 1.0):
    p, q = ETA ** (0.5 / l), ETA * 0.5 / l
    a1.annotate(f"{p:,.3g}", (l, p), xytext=(5 if l < 1 else -5, 6), textcoords='offset points', ha='left' if l < 1 else 'right', fontsize=9, color=T1,
                bbox=dict(boxstyle='square,pad=0.15', fc=S, ec='none'), zorder=5)
    a1.annotate(f"{q:,.3g}", (l, q), xytext=(6 if l == 0.1 else -6, -30 if l == 0.1 else -16), textcoords='offset points', ha='left' if l == 0.1 else 'right',
                fontsize=9, color=T1, bbox=dict(boxstyle='square,pad=0.15', fc=S, ec='none'), zorder=5)
    a1.plot([l, l], [p, p], marker='o', ms=4, color=C['power']); a1.plot([l, l], [q, q], marker='o', ms=4, color=C['linear'])
a1.legend(frameon=False, fontsize=10, loc='upper right', labelcolor=T1)
fig.text(0.1, 0.03, "η = Coding Automation Efficiency Improvement Factor, default 3. Both forms equal 3 at λ 0.5;\n"
         "their slopes there differ by a factor of ln 3 ≈ 1.1, so they stay close for λ 0.5 to 1\nand separate fast below about 0.3.", fontsize=8.5, color=MUTED, ha='left')
fig.savefig('eta-adjustment-forms.png', dpi=180)
