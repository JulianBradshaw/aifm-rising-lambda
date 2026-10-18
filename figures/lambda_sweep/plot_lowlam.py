import csv, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
S, T1, T2, MUTED, GRID = '#fcfcfb', '#0b0b0b', '#52514e', '#8a8984', '#e6e5e0'
C = {'ac_year':'#2a78d6', 'asi_year':'#eb6834'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.edgecolor':MUTED,
  'axes.labelcolor':T2,'xtick.color':T2,'ytick.color':T2,'figure.facecolor':S,'axes.facecolor':S})
rows = list(csv.DictReader(open('lambda_sweep_low.csv')))
FLOOR = 0.06
MON = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
def ylab(y):
    yr = int(y); m = round((y-yr)*12)
    if m == 12: yr, m = yr+1, 0
    return f"{MON[m]} {yr}"
PRESETS = [('daniel-08-16-26',"Daniel's preset"),('eli-08-16-26',"Eli's preset"),('brendan-08-16-26',"Brendan's preset")]
MODES = [('uplift-solved','Coding uplift anchor (the presets\' default)'),('time-horizon','Time horizon anchor'),('revenue','Revenue anchor')]
TODAY = 2026.578082
fig, axes = plt.subplots(3, 3, figsize=(14,15.6), sharey=True, sharex=True)
fig.subplots_adjust(left=0.09, right=0.985, top=0.9, bottom=0.085, wspace=0.08, hspace=0.3)
for r_i, (mode, mlabel) in enumerate(MODES):
    for c_i, (pid, title) in enumerate(PRESETS):
        ax = axes[r_i][c_i]
        ax.axvspan(0.3, 1.03, color='#f0efea', zorder=0, lw=0)
        ax.axhline(TODAY, color=MUTED, lw=0.8, zorder=1)
        for form, ls in [('linear',(0,(4,2.5))),('model','-')]:
            r = [x for x in rows if x['preset']==pid and x['ac_anchor_mode']==mode and x['eta_form']==form
                 and float(x['parallel_penalty']) >= FLOOR - 1e-9]
            x = [float(v['parallel_penalty']) for v in r]
            for key, name in [('ac_year','AC'),('asi_year','ASI')]:
                y = [float(v[key]) for v in r]
                ax.plot(x, y, color=C[key], lw=2 if form=='model' else 1.6, ls=ls,
                        marker='o' if form=='model' else None, ms=3, zorder=3 if form=='model' else 2)
                if form == 'model':
                    i10 = x.index(0.1)
                    ax.annotate(ylab(y[i10]), (0.1,y[i10]), xytext=(4,7 if key=='asi_year' else -13), textcoords='offset points',
                                ha='left', fontsize=8.5, color=T2)
                    ax.annotate(f"{name} {ylab(y[-1])}", (x[-1],y[-1]), xytext=(-4,9), textcoords='offset points', ha='right', color=T1, fontsize=9.5)
        ax.set_title(title, loc='left', fontsize=10.5, color=T2)
        if c_i == 0: ax.text(-0.2, 1.2 if r_i == 0 else 1.13, mlabel, transform=ax.transAxes, va='bottom', ha='left', fontsize=13, color=T1, weight='bold')
        ax.set_xlim(0.03, 1.03); ax.set_xticks([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0])
        ax.set_xticklabels(['0.1','0.2','0.3','0.4','0.5','0.6','0.7','0.8','0.9','1'], fontsize=9)
        ax.grid(axis='y', color=GRID, lw=0.8); ax.set_axisbelow(True)
        for s in ('top','right'): ax.spines[s].set_visible(False)
        if r_i == 2: ax.set_xlabel('λ', fontsize=13)
        ax.axvline(0.5, color=MUTED, lw=1, ls=(0,(2,3)), zorder=1)
        if r_i == 0 and c_i == 0:
            ax.text(0.31, 2035.4, 'λ range of the\nearlier figures', fontsize=8.5, color=T2, va='top')
            ax.text(0.49, 2033.6, 'λ 0.5\ndefault', fontsize=8.5, color=T2, va='top', ha='right')
            ax.text(0.98, TODAY+0.12, f'today ({ylab(TODAY)})', fontsize=8.5, color=T2, ha='right', va='bottom')
        if r_i == 0:
            top = ax.secondary_xaxis('top')
            ticks = [0.1,0.2,0.3,0.5,1.0]
            top.set_xticks(ticks); top.set_xticklabels([f"{3**(0.5/l):,.0f}" if 3**(0.5/l) > 20 else f"{3**(0.5/l):.1f}" for l in ticks], fontsize=8.5, color=T2)
            top.tick_params(length=3, color=MUTED); top.spines['top'].set_color(MUTED)
            if c_i == 0: top.set_xlabel("model's effective η = 3^(0.5/λ)", fontsize=9, color=T2, labelpad=4)
yt = list(range(2027, 2036))
axes[0][0].set_yticks(yt); axes[0][0].set_yticklabels([f"Jan {v}" for v in yt]); axes[0][0].set_ylim(2026.3, 2035.5)
handles = [Line2D([],[],color=C['ac_year'],lw=2,marker='o',ms=3,label='AC, model (η^(0.5/λ))'),
           Line2D([],[],color=C['ac_year'],lw=1.6,ls=(0,(4,2.5)),label="AC, proposed linear correction (η·0.5/λ)"),
           Line2D([],[],color=C['asi_year'],lw=2,marker='o',ms=3,label='ASI, model (η^(0.5/λ))'),
           Line2D([],[],color=C['asi_year'],lw=1.6,ls=(0,(4,2.5)),label="ASI, proposed linear correction (η·0.5/λ)")]
fig.legend(handles=handles, loc='upper left', bbox_to_anchor=(0.085, 0.997), ncol=2, frameon=False, fontsize=10, labelcolor=T1)
fig.text(0.09, 0.02, "AC = Automated Coder; ASI = Artificial Superintelligence. Effective η at λ 0.1: model 243, proposed correction 15. "
  f"Floor λ {FLOOR}: below it the coding uplift anchor's\ncalibration fails or jumps erratically under either η form. "
  "AI Futures Model (aifm-public, commit 1c40ecdb), 08/16/26 presets, single runs at each preset's median parameters; only λ, the AC anchor\nmode and the η adjustment varied.",
  fontsize=8.5, color=MUTED, ha='left')
fig.savefig('lambda-sweep-dates-anchors-low.png', dpi=170)
