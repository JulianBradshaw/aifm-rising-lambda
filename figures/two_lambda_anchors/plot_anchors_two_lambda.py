import csv, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
S, T1, T2, MUTED, GRID = '#fcfcfb', '#0b0b0b', '#52514e', '#8a8984', '#e6e5e0'
C = {'ac_year':'#2a78d6', 'asi_year':'#eb6834'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.edgecolor':MUTED,
  'axes.labelcolor':T2,'xtick.color':T2,'ytick.color':T2,'figure.facecolor':S,'axes.facecolor':S})
rows = list(csv.DictReader(open('lambda_sweep_anchors_two_lambda.csv')))
orig = list(csv.DictReader(open('../lambda_sweep/lambda_sweep_anchors.csv')))
MON = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
def ylab(y):
    yr = int(y); m = round((y-yr)*12)
    if m == 12: yr, m = yr+1, 0
    return f"{MON[m]} {yr}"
PRESETS = [('daniel-08-16-26',"Daniel's preset"),('eli-08-16-26',"Eli's preset"),('brendan-08-16-26',"Brendan's preset")]
MODES = [('uplift-solved','Coding uplift anchor (the presets\' default)'),('time-horizon','Time horizon anchor'),('revenue','Revenue anchor')]
fig, axes = plt.subplots(3, 3, figsize=(14,15), sharey=True, sharex=True)
fig.subplots_adjust(left=0.09, right=0.985, top=0.95, bottom=0.08, wspace=0.08, hspace=0.3)
for r_i, (mode, mlabel) in enumerate(MODES):
    for c_i, (pid, title) in enumerate(PRESETS):
        ax = axes[r_i][c_i]
        r = [x for x in rows if x['preset']==pid and x['ac_anchor_mode']==mode]
        x = [float(v['lambda_forward']) for v in r]
        o = [v for v in orig if v['preset']==pid and v['ac_anchor_mode']==mode]
        for key in ('ac_year','asi_year'):
            ax.plot([float(v['parallel_penalty']) for v in o], [float(v[key]) for v in o], color=C[key], lw=1.2, ls=(0,(4,3)), alpha=0.45, zorder=2)
        for key, name in [('ac_year','AC'),('asi_year','ASI')]:
            y = [float(v[key]) for v in r]
            ax.plot(x, y, color=C[key], lw=2, marker='o', ms=3.5, zorder=3)
            ax.annotate(f"{name} {ylab(y[-1])}", (x[-1],y[-1]), xytext=(-4,9), textcoords='offset points', ha='right', color=T1, fontsize=9.5)
            ax.annotate(ylab(y[4]), (0.5,y[4]), xytext=(-6,6), textcoords='offset points', ha='right', fontsize=8.5, color=T2)
        ax.set_title(title, loc='left', fontsize=10.5, color=T2)
        if c_i == 0: ax.text(-0.2, 1.13, mlabel, transform=ax.transAxes, va='bottom', ha='left', fontsize=13, color=T1, weight='bold')
        ax.set_xlim(0.27, 1.03); ax.set_xticks([0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0])
        ax.grid(axis='y', color=GRID, lw=0.8); ax.set_axisbelow(True)
        for s in ('top','right'): ax.spines[s].set_visible(False)
        if r_i == 2: ax.set_xlabel('Forward λ (history and calibration stay at 0.5)', fontsize=12)
        for gx, lab in [(0.5,'λ 0.5\nAI Futures\nModel default'),(0.65,'λ 0.65\nfork\nestimated')]:
            ax.axvline(gx, color=MUTED, lw=1, ls=(0,(2,3)), zorder=1)
            if r_i == 0 and c_i == 0:
                ax.text(gx-0.008 if gx == 0.5 else gx+0.008, 2034.9, lab, fontsize=8.5, color=T2, va='top', ha='right' if gx == 0.5 else 'left')
yt = list(range(2027, 2036))
axes[0][0].set_yticks(yt); axes[0][0].set_yticklabels([f"Jan {v}" for v in yt]); axes[0][0].set_ylim(2027, 2035)
fig.text(0.09, 0.015, "AC = Automated Coder; ASI = Artificial Superintelligence. Solid: two-λ variant (aifm-lambda-fixes, η rescaled linearly). Faint dashed: the original model with one λ.\n"
  "Two-λ variant of the AI Futures Model (aifm-public, commit 1c40ecdb): history and calibration at λ 0.5, forward λ for coding labor growth from today.\n"
  "08/16/26 presets, single runs at each preset's median parameters; only the forward λ and the AC anchor mode varied.",
  fontsize=8.5, color=MUTED, ha='left')
fig.savefig('lambda-sweep-dates-anchors-two-lambda.png', dpi=170)
