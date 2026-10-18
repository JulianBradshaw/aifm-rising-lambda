import csv, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
S, T1, T2, MUTED, GRID = '#fcfcfb', '#0b0b0b', '#52514e', '#8a8984', '#e6e5e0'
C = {'ac_year':'#2a78d6', 'asi_year':'#eb6834'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.edgecolor':MUTED,
  'axes.labelcolor':T2,'xtick.color':T2,'ytick.color':T2,'figure.facecolor':S,'axes.facecolor':S})
rows = list(csv.DictReader(open('lambda_sweep_presets.csv')))
MON = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
def ylab(y):
    yr = int(y); m = round((y-yr)*12)
    if m == 12: yr, m = yr+1, 0
    return f"{MON[m]} {yr}"
PRESETS = [('daniel-08-16-26',"Daniel's preset"),('eli-08-16-26',"Eli's preset"),('brendan-08-16-26',"Brendan's preset")]
fig, axes = plt.subplots(1, 3, figsize=(14,6.4), sharey=True)
fig.subplots_adjust(left=0.07, right=0.985, top=0.93, bottom=0.17, wspace=0.08)
for i, (ax, (pid, title)) in enumerate(zip(axes, PRESETS)):
    r = [x for x in rows if x['preset']==pid]
    x = [float(v['parallel_penalty']) for v in r]
    for key, name in [('ac_year','AC'),('asi_year','ASI')]:
        y = [float(v[key]) for v in r]
        ax.plot(x, y, color=C[key], lw=2, marker='o', ms=3.5, zorder=3)
        ax.annotate(f"{name} {ylab(y[-1])}", (x[-1],y[-1]), xytext=(-4,9), textcoords='offset points', ha='right', color=T1, fontsize=9.5)
        ax.annotate(ylab(y[4]), (0.5,y[4]), xytext=(-6,6), textcoords='offset points', ha='right', fontsize=8.5, color=T2)
    ax.set_title(title, loc='left', fontsize=12, color=T1, weight='bold')
    ax.set_xlim(0.27, 1.03); ax.set_xticks([0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0])
    ax.grid(axis='y', color=GRID, lw=0.8); ax.set_axisbelow(True)
    for s in ('top','right'): ax.spines[s].set_visible(False)
    ax.set_xlabel('λ', fontsize=13)
    for gx, lab in [(0.5,'λ 0.5\nAI Futures\nModel default'),(0.65,'λ 0.65\nfork\nestimated')]:
        ax.axvline(gx, color=MUTED, lw=1, ls=(0,(2,3)), zorder=1)
        if i == 0: ax.text(gx-0.008 if gx == 0.5 else gx+0.008, 2034.4, lab, fontsize=8.5, color=T2, va='top', ha='right' if gx == 0.5 else 'left')
yt = list(range(2027, 2035))
axes[0].set_yticks(yt); axes[0].set_yticklabels([f"Jan {v}" for v in yt]); axes[0].set_ylim(2027, 2034.5)
fig.text(0.07, 0.035, "AC = Automated Coder; ASI = Artificial Superintelligence.\n"
  "AI Futures Model (aifm-public, commit 1c40ecdb), 08/16/26 presets, single runs at each preset's median parameters; only λ varied.",
  fontsize=8.5, color=MUTED, ha='left')
fig.savefig('lambda-sweep-dates-presets.png', dpi=200)
