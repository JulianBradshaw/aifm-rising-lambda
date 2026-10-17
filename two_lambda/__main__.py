"""Two-λ variant against the single-λ model. Run: python -m two_lambda [--preset NAME] [--output DIR].

For each anchor and forward λ, writes AC, ASI and takeoff for the two-λ variant (η rescaled
linearly, by upstream's power form, or not at all) and for the unmodified model with that λ
everywhere. Native present day; deterministic single runs at preset medians.
"""
import argparse
import csv
from pathlib import Path
from . import ROOT
from .model import Variant, simulate, upstream_single_lambda
from .presets import PRESETS

ANCHORS = ('uplift-solved', 'time-horizon', 'revenue')
LAMBDAS = (0.5, 0.65, 0.8, 1.0)


def month(value):
    if value is None:
        return 'not reached'
    # Site-style approximate month: decimal years are not calendar day timestamps.
    year = int(value)
    return f'{year}-{min(12, 1+int((value-year)*12)):02d}'


CASES = [('two-λ, η linear', 'linear'), ('two-λ, η power', 'power'), ('two-λ, η not rescaled', 'none'),
         ('single λ (upstream)', None)]


def run(preset):
    rows = []
    for anchor in ANCHORS:
        for lam in LAMBDAS:
            for label, eta in CASES:
                r = (upstream_single_lambda(lam, anchor, preset=preset) if eta is None
                     else simulate(Variant(lam, eta), anchor, preset=preset))
                m = r['milestones']
                rows.append({'preset': preset, 'anchor': anchor, 'lambda_forward': lam, 'case': label,
                    'AC': m['AC'], 'ASI': m['ASI'], 'takeoff_months': r['takeoff_months'],
                    'r_software': r['r_software'], 'automation_fraction_t0': r['automation_fraction_t0'],
                    'parallel_labor_per_human_t0': r['parallel_labor_per_human_t0'], 'eta_forward': r['eta_forward']})
    return rows


def write_report(rows, output, preset):
    get = {(r['anchor'], r['lambda_forward'], r['case']): r for r in rows}
    fmt = lambda v, d=1: '—' if v is None else f'{v:.{d}f}'
    lines = [f'# Two-λ variant ({preset}, native present day)', '',
        'One λ (the preset’s 0.5) for history and calibration, a separate forward λ for coding labor from today on. '
        'Today’s automation fraction, AI labor and r_software are therefore the same at every forward λ. '
        'The single-λ rows are the unmodified model with that λ everywhere. Takeoff is AC to ASI in months; '
        'deterministic single runs at preset medians, not forecasts. Regenerate with `python -m two_lambda`.', '']
    for anchor in ANCHORS:
        lines += [f'## {anchor}', '', '| | ' + ' | '.join(f'λ {lam:g}' for lam in LAMBDAS) + ' |', '| --- |' + ' --- |'*len(LAMBDAS)]
        for label, _ in CASES:
            cells = [get[anchor, lam, label] for lam in LAMBDAS]
            lines.append(f'| {label} | ' + ' | '.join(
                f"{fmt(c['takeoff_months'])} mo (AC {month(c['AC'])}, ASI {month(c['ASI'])})" for c in cells) + ' |')
        single = [get[anchor, lam, CASES[-1][0]] for lam in LAMBDAS]
        two = get[anchor, LAMBDAS[-1], CASES[0][0]]
        lines += ['', f"r_software {two['r_software']:.3f} and automation today {100*two['automation_fraction_t0']:.0f}% "
            f"(parallel coding labor {two['parallel_labor_per_human_t0']:.2f}× human) at every forward λ; the single-λ model gives "
            + ', '.join(f"{s['r_software']:.3f} / {100*s['automation_fraction_t0']:.0f}% / {s['parallel_labor_per_human_t0']:.2f}×"
                        for s in single) + f" at λ {', '.join(f'{lam:g}' for lam in LAMBDAS)}.", '']
    (output/'REPORT.md').write_text('\n'.join(lines), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--preset', default='daniel-08-16-26', choices=PRESETS)
    parser.add_argument('--output', type=Path, default=ROOT/'outputs')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    rows = run(args.preset)
    with open(args.output/'results.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    write_report(rows, args.output, args.preset)
    print(f'Wrote {len(rows)} runs to {args.output.relative_to(ROOT) if args.output.is_relative_to(ROOT) else args.output.name}')


if __name__ == '__main__':
    main()
