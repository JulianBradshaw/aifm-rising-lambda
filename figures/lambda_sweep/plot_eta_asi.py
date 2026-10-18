# Months the η adjustment moves the ASI date, relative to the proposed linear η·(0.5/λ), from lambda_sweep_low.csv.
import csv, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
S, T1, T2, MUTED, GRID = '#fcfcfb', '#0b0b0b', '#52514e', '#8a8984', '#e6e5e0'
C = {'model':'#eb6834', 'none':'#2a78d6'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.edgecolor':MUTED,
  'axes.labelcolor':T2,'xtick.color':T2,'ytick.color':T2,'figure.facecolor':S,'axes.facecolor':S})
rows = list(csv.DictReader(open('lambda_sweep_low.csv')))
FLOOR = 0.06
TODAY = 2026.578082
PRESETS = [('daniel-08-16-26',"Daniel's preset"),('eli-08-16-26',"Eli's preset"),('brendan-08-16-26',"Brendan's preset")]
MODES = [('uplift-solved','Coding uplift anchor (the presets\' default)'),('time-horizon','Time horizon anchor'),('revenue','Revenue anchor')]
def get(pid, mode, form):
    return {float(x['parallel_penalty']): float(x['asi_year']) for x in rows if x['preset']==pid and x['ac_anchor_mode']==mode
            and x['eta_form']==form and x['asi_year'] and float(x['ac_year']) >= TODAY and float(x['parallel_penalty']) >= FLOOR - 1e-9}
fig, axes = plt.subplots(3, 3, figsize=(14,14), sharey=True, sharex=True)
fig.subplots_adjust(left=0.08, right=0.985, top=0.88, bottom=0.09, wspace=0.08, hspace=0.32)
for r_i, (mode, mlabel) in enumerate(MODES):
    for c_i, (pid, title) in enumerate(PRESETS):
        ax = axes[r_i][c_i]
        base = get(pid, mode, 'linear')
        ax.axhline(0, color=C['none'], lw=2, zorder=2)
        ax.axvline(0.5, color=MUTED, lw=1, ls=(0,(2,3)), zorder=1)
        for form in ['model']:
            d = get(pid, mode, form); x = sorted(l for l in d if l in base)
            y = [12*(base[l]-d[l]) for l in x]
            ax.plot(x, y, color=C[form], lw=2, marker='o', ms=3, zorder=3)
            if form == 'model':
                lmin = x[y.index(max(y))]
                for l in (lmin, 1.0):
                    v = y[x.index(l)]
                    ax.annotate(f"{v:.1f} mo earlier", (l, v), xytext=(4 if l < 0.5 else -4, 8), textcoords='offset points',
                                ha='left' if l < 0.5 else 'right', fontsize=9, color=T1)
        ax.set_title(title, loc='left', fontsize=10.5, color=T2)
        if c_i == 0: ax.text(-0.2, 1.2 if r_i == 0 else 1.13, mlabel, transform=ax.transAxes, va='bottom', ha='left', fontsize=13, color=T1, weight='bold')
        ax.set_xlim(0.03, 1.03); ax.set_xticks([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0])
        ax.set_xticklabels(['0.1','0.2','0.3','0.4','0.5','0.6','0.7','0.8','0.9','1'], fontsize=9)
        ax.grid(axis='y', color=GRID, lw=0.8); ax.set_axisbelow(True)
        for s in ('top','right'): ax.spines[s].set_visible(False)
        if r_i == 2: ax.set_xlabel('λ', fontsize=13)
        if c_i == 0: ax.set_ylabel('ASI earlier by, months', fontsize=10)
        if r_i == 0:
            top = ax.secondary_xaxis('top'); ticks = [0.1,0.2,0.3,0.5,1.0]
            top.set_xticks(ticks); top.set_xticklabels([f"{3**(0.5/l):,.0f}" if 3**(0.5/l) > 20 else f"{3**(0.5/l):.1f}" for l in ticks], fontsize=8.5, color=T2)
            top.tick_params(length=3, color=MUTED); top.spines['top'].set_color(MUTED)
            if c_i == 0: top.set_xlabel("model's effective η = 3^(0.5/λ)", fontsize=9, color=T2, labelpad=4)
        if r_i == 0 and c_i == 0:
            ax.text(0.51, 4.4, 'λ 0.5: both\nforms agree', fontsize=8.5, color=T2, va='top')
axes[0][0].set_ylim(-1.5, 4.5)
handles = [Line2D([],[],color=C['model'],lw=2,marker='o',ms=3,label='Model, η^(0.5/λ)'),
           Line2D([],[],color=C['none'],lw=2,label='Corrected model, η·(0.5/λ)')]
fig.text(0.08, 0.985, 'Shifts in ASI date due to η adjustment', fontsize=16, color=T1, weight='bold', va='top')
fig.legend(handles=handles, loc='upper left', bbox_to_anchor=(0.075, 0.965), ncol=2, frameon=False, fontsize=10, labelcolor=T1)
fig.text(0.08, 0.02, "ASI = Artificial Superintelligence. The orange line is how many months earlier ASI arrives under the model's η^(0.5/λ) than under η·(0.5/λ), same preset, anchor and λ.\n"
  "Under the model's form AC moves by under half a month in every case, so these shifts are almost entirely takeoff length. Floor λ 0.06.\n"
  "AI Futures Model (aifm-public, commit 1c40ecdb), 08/16/26 presets, single runs at each preset's median parameters; only λ, the AC anchor mode and the η adjustment varied.",
  fontsize=8.5, color=MUTED, ha='left')
fig.savefig('lambda-eta-asi-shift.png', dpi=170)
