import csv, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
S, T1, T2, MUTED, GRID = '#fcfcfb', '#0b0b0b', '#52514e', '#8a8984', '#e6e5e0'
C1, C2 = '#2a78d6', '#eb6834'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.edgecolor':MUTED,
  'axes.labelcolor':T2,'xtick.color':T2,'ytick.color':T2,'figure.facecolor':S,'axes.facecolor':S})
rows = list(csv.DictReader(open('lambda_sweep.csv')))
def series(setting, key):
    r = [x for x in rows if x['setting'].startswith(setting)]
    return [float(x['parallel_penalty']) for x in r], [float(x[key]) for x in r]
MON = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
def ylab(y):
    yr = int(y); m = round((y-yr)*12); 
    if m == 12: yr, m = yr+1, 0
    return f"{MON[m]} {yr}"

def base(ax, title, sub):
    ax.set_xlim(0.28, 1.02)
    ax.set_xticks([0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0])
    ax.grid(axis='y', color=GRID, lw=0.8); ax.set_axisbelow(True)
    for s in ('top','right'): ax.spines[s].set_visible(False)
    ax.set_xlabel('λ', fontsize=13)

def guides(ax, ytop):
    for x, lab in [(0.5,'λ 0.5\nAI Futures\nModel default'),(0.65,'λ 0.65\nfork\nestimated')]:
        ax.axvline(x, color=MUTED, lw=1, ls=(0,(2,3)), zorder=1)
        ax.text(x+0.007, ytop, lab, fontsize=9, color=T2, va='top', ha='left')

def legend(ax):
    h = [Line2D([],[],color=T2,lw=2,label='Native present day (Aug 2026)'),
         Line2D([],[],color=T2,lw=2,ls=(0,(4,2)),label='Present day overridden to 2025.6')]
    ax.legend(handles=h, loc='lower right', frameon=False, fontsize=9, labelcolor=T2)

FOOT = ("AC = Automated Coder; ASI = Artificial Superintelligence.\n"
        "AI Futures Model (aifm-public, commit 1c40ecdb), Daniel 08/16/26 preset, single runs at the preset's median parameters; only λ varied.")

# Figure 1: dates
fig, ax = plt.subplots(figsize=(9,5.8)); fig.subplots_adjust(left=0.12, right=0.86, top=0.95, bottom=0.17)
for key, c, name in [('ac_year',C1,'AC'),('asi_year',C2,'ASI')]:
    x,y = series('native',key); ax.plot(x,y,color=c,lw=2,marker='o',ms=4,zorder=3)
    ax.annotate(f"{name}  {ylab(y[-1])}", (x[-1],y[-1]), xytext=(8,0), textcoords='offset points', va='center', color=T1, fontsize=10)
    x2,y2 = series('present day 2025.6',key); ax.plot(x2,y2,color=c,lw=1.5,ls=(0,(4,2)),zorder=2)
yt = [2027.0,2027.5,2028.0,2028.5,2029.0,2029.5,2030.0]
ax.set_yticks(yt); ax.set_yticklabels([ylab(v) for v in yt]); ax.set_ylim(2027.0, 2030.15)
guides(ax, 2030.12)
for key,name in [('ac_year','AC'),('asi_year','ASI')]:
    _,y = series('native',key)
    ax.annotate(ylab(y[4]), (0.5,y[4]), xytext=(-8,8), textcoords='offset points', ha='right', fontsize=9, color=T2)
legend(ax)
base(ax, 'Higher λ pushes both AC and ASI later in the AI Futures Model',
     'Date of Automated Coder (AC) and Artificial Superintelligence (ASI) versus λ')
fig.text(0.07, 0.03, FOOT, fontsize=8, color=MUTED, ha='left')
fig.savefig('lambda-sweep-dates.png', dpi=200)

# Figure 2: durations
fig, ax = plt.subplots(figsize=(9,5.8)); fig.subplots_adjust(left=0.1, right=0.84, top=0.95, bottom=0.17)
for key, c, name in [('months_aug2026_to_ac',C1,'Aug 2026 → AC'),('months_ac_to_asi',C2,'AC → ASI')]:
    x,y = series('native',key); ax.plot(x,y,color=c,lw=2,marker='o',ms=4,zorder=3)
    ax.annotate(f"{name}\n{y[-1]:.1f} mo", (x[-1],y[-1]), xytext=(8,0), textcoords='offset points', va='center', color=T1, fontsize=10)
    off = (-6,6) if key.startswith('months_aug') else (-6,-12)
    ax.annotate(f"{y[4]:.1f}", (0.5,y[4]), xytext=off, textcoords='offset points', ha='right' if off[0]<0 else 'left', fontsize=9, color=T2)
    x2,y2 = series('present day 2025.6',key); ax.plot(x2,y2,color=c,lw=1.5,ls=(0,(4,2)),zorder=2)
ax.set_ylim(0, 26); ax.set_ylabel('Months')
guides(ax, 25.8)
legend(ax)
base(ax, 'Higher λ lengthens both the wait for AC and the AC → ASI takeoff',
     'Months from Aug 2026 to AC, and months from AC to ASI, versus λ')
fig.text(0.07, 0.03, FOOT, fontsize=8, color=MUTED, ha='left')
fig.savefig('lambda-sweep-durations.png', dpi=200)
