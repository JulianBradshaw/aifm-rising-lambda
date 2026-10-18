"""Timelines when λ rises over time. Run: python -m two_lambda.rising_sweep [--preset NAME] [--output DIR].

Runs a few λ schedules (fixed, the 2024-to-today trend continued, and a fast ramp to 1) and
writes AC, ASI and takeoff to rising_lambda.csv, a table to RISING.md and, if matplotlib is
installed, a figure to rising-lambda.png. Native present day; deterministic single runs.
"""
import argparse
import csv
from dataclasses import replace
from pathlib import Path
import numpy as np
from . import ROOT
from .model import Variant, simulate, calibrate, calibration_end
from .presets import PRESETS
from .__main__ import month

LAMBDA_2024, LAMBDA_TODAY, LAMBDA_CAP = 0.5, 0.65, 1.0
# λ 0.5 stands for mid-2024, the year the r_software fit describes.
TREND_START = 2024.5


def cases(t0):
    """(key, label, Variant or None for the schedule's own reference, kind) in drawing order."""
    slope = (LAMBDA_TODAY - LAMBDA_2024) / (t0 - TREND_START)
    return [
        ('fixed-0.5', 'Fixed λ 0.5', Variant(0.5), 'reference'),
        ('flat-0.65', 'Flat at 0.65 from today', Variant(LAMBDA_TODAY), 'main'),
        ('trend', f'2024–26 trend (+{slope:.3f}/yr), capped at 1', Variant(
            LAMBDA_TODAY, lambda_end=LAMBDA_CAP, ramp_years=(LAMBDA_CAP - LAMBDA_TODAY) / slope), 'main'),
        ('swarm-ramp', 'Ramp to 1 over 2027 (aifm-swarm shape)', Variant(
            LAMBDA_TODAY, lambda_end=LAMBDA_CAP, ramp_start=2027.0, ramp_years=0.75, ramp_shape='smoothstep'), 'main'),
        ('fixed-1', 'Fixed λ 1 from today', Variant(1.0), 'reference'),
    ]


def run(preset, anchor, eta_rescales=('linear', 'none')):
    t0 = calibration_end(calibrate(anchor, preset=preset))
    rows = []
    for eta in eta_rescales:
        for key, label, variant, kind in cases(t0):
            v = replace(variant, eta_rescale=eta)
            r = simulate(v, anchor, preset=preset)
            m = r['milestones']
            rows.append({'preset': preset, 'anchor': anchor, 'case': key, 'label': label, 'kind': kind,
                'eta_rescale': eta, 'lambda_today': v.lambda_forward, 'lambda_end': v.lambda_end,
                'ramp_start': v.ramp_window(t0)[0] if v.rising else None, 'ramp_years': v.ramp_years if v.rising else None,
                'ramp_shape': v.ramp_shape if v.rising else None,
                'lambda_AC': r['lambda_at'].get('AC'), 'lambda_ASI': r['lambda_at'].get('ASI'),
                'AC': m['AC'], 'ASI': m['ASI'], 'takeoff_months': r['takeoff_months']})
    return t0, rows


def table(rows):
    lines = ['| Schedule | λ at AC | λ at ASI | AC | ASI | Takeoff |', '| --- | --- | --- | --- | --- | --- |']
    for r in rows:
        t = r['takeoff_months']
        lines.append(f"| {r['label']} | {r['lambda_AC']:.2f} | {r['lambda_ASI']:.2f} | {month(r['AC'])} | {month(r['ASI'])} | "
                     f"{'—' if t is None else f'{t:.1f}'} mo |")
    return lines


def figure(t0, rows, path):
    """λ schedules on the left; AC to ASI for each on the right."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FixedLocator, FuncFormatter
    ink, muted, grid = '#1f1f1e', '#6b6a64', '#e8e7e2'
    # Rising schedules in teals, fixed references in neutral grays.
    colors = {'fixed-0.5': '#9a9993', 'flat-0.65': '#0b6e69', 'trend': '#2a9d8f', 'swarm-ramp': '#7cc5bb', 'fixed-1': '#5f5e59'}
    styles = {'fixed-0.5': (0, (1.5, 2.5)), 'fixed-1': (0, (1.5, 2.5))}
    rows = [r for r in rows if r['eta_rescale'] == 'linear']
    variants = {k: v for k, _, v, _ in cases(t0)}
    fig, (left, right) = plt.subplots(1, 2, figsize=(11, 5), constrained_layout=True, facecolor='white',
                                      gridspec_kw={'width_ratios': [1, 1.25]})
    for ax in (left, right):
        for side in ('top', 'right'):
            ax.spines[side].set_visible(False)
        for side in ('left', 'bottom'):
            ax.spines[side].set_color(muted)
        ax.tick_params(colors=muted, labelcolor=muted, labelsize=10)
        ax.set_axisbelow(True)
    left.grid(True, axis='y', color=grid, lw=0.8)
    ts = np.linspace(TREND_START, 2032, 600)
    hist = ts <= t0
    left.plot(ts[hist], LAMBDA_2024 + (LAMBDA_TODAY - LAMBDA_2024) * (ts[hist] - TREND_START) / (t0 - TREND_START),
              color=muted, lw=1.4, ls=(0, (4, 3)))
    left.annotate('evidence, mid-2024 to today', (TREND_START + 0.75, 0.5), color=muted, fontsize=9, rotation=17)
    future = ts[ts >= t0]
    for r in rows:
        v = variants[r['case']]
        left.plot(future, [v.lambda_at(t, t0) for t in future], color=colors[r['case']], lw=2.2,
                  ls=styles.get(r['case'], '-'), solid_capstyle='round')
    left.axvline(t0, color=grid, lw=1)
    left.annotate('today', (t0, 1.03), ha='center', color=muted, fontsize=9)
    left.set_ylim(0.45, 1.06)
    left.set_xlim(TREND_START, 2032)
    left.set_ylabel('Forward λ', color=ink, fontsize=10)
    left.set_title('λ schedules', color=ink, fontsize=11, loc='left')

    right.grid(True, axis='x', color=grid, lw=0.8)
    for i, r in enumerate(rows):
        y = len(rows) - 1 - i
        c = colors[r['case']]
        right.plot([r['AC'], r['ASI']], [y, y], color=c, lw=6, solid_capstyle='butt', alpha=0.9)
        right.annotate(f"{r['takeoff_months']:.1f} mo", (r['ASI'], y), xytext=(6, -4), textcoords='offset points', color=ink, fontsize=9.5)
        right.annotate(r['label'], (r['AC'], y), xytext=(0, 7), textcoords='offset points', color=ink, fontsize=9.5)
    lo, hi = min(r['AC'] for r in rows), max(r['ASI'] for r in rows)
    ticks = [y + q for y in range(int(lo), int(hi) + 2) for q in (0, 0.25, 0.5, 0.75) if lo - 0.15 <= y + q <= hi + 0.3]
    right.xaxis.set_major_locator(FixedLocator(ticks))
    right.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{['Jan', 'Apr', 'Jul', 'Oct'][int(round((v % 1) * 4)) % 4]} {int(v)}"))
    right.set_xlim(lo - 0.15, hi + 0.35)
    right.set_yticks([])
    right.spines['left'].set_visible(False)
    right.set_ylim(-0.6, len(rows) - 0.2)
    right.set_title('AC (bar start) to ASI (bar end)', color=ink, fontsize=11, loc='left')
    r0 = rows[0]
    names = {'daniel-08-16-26': 'Daniel (Aug 2026) preset', 'eli-08-16-26': 'Eli (Aug 2026) preset',
             'brendan-08-16-26': 'Brendan (Aug 2026) preset'}
    anchors = {'uplift-solved': 'Coding Uplift anchor', 'time-horizon': 'Time Horizon anchor', 'revenue': 'Revenue anchor', 'eci': 'ECI anchor'}
    fig.suptitle(f"λ rising after today shortens takeoff by up to two months and barely moves AC\n"
                 f"{names.get(r0['preset'], r0['preset'])}, {anchors.get(r0['anchor'], r0['anchor'])}, "
                 f"two-λ fixes, η rescaled for today's λ",
                 color=ink, fontsize=11.5, x=0.01, ha='left')
    fig.savefig(path, dpi=160, facecolor='white')
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--preset', default='daniel-08-16-26', choices=PRESETS)
    parser.add_argument('--anchor', default='uplift-solved')
    parser.add_argument('--output', type=Path, default=ROOT/'outputs')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    t0, rows = run(args.preset, args.anchor)
    with open(args.output/'rising_lambda.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    linear = [r for r in rows if r['eta_rescale'] == 'linear']
    none = [r for r in rows if r['eta_rescale'] == 'none']
    lines = [f'# λ rising over time ({args.preset}, {args.anchor} anchor)', '',
        f'History and calibration keep λ 0.5. From the calibration date ({t0:.2f}) the forward λ starts at 0.65 and '
        'follows each schedule; serial coding labor grows as λ(t) times the growth of parallel labor, so a later rise '
        'applies only to growth after it. η is rescaled for today\'s λ (0.5/0.65) and not for the later rise. '
        'Takeoff is AC to ASI; deterministic single runs at preset medians, not forecasts. '
        'Regenerate with `python -m two_lambda.rising_sweep`.', '', *table(linear), '',
        'With η not rescaled at all (the other bound used in the two-λ results):', '', *table(none), '',
        '![λ schedules and AC to ASI for each](rising-lambda.png)', '']
    (args.output/'RISING.md').write_text('\n'.join(lines), encoding='utf-8')
    try:
        figure(t0, rows, args.output/'rising-lambda.png')
    except ImportError:
        print('matplotlib not installed; skipped the figure')
    print('\n'.join(table(linear)))


if __name__ == '__main__':
    main()
