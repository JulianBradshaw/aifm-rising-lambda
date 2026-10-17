"""Browser entry point: runs two_lambda inside Pyodide and returns JSON for the page.

The model code is the same package the command line uses (unpacked from model.zip). Each call
returns three runs: the preset at its own λ, the two-λ variant at the chosen forward λ, and the
original model with that λ everywhere. 'legacy' dates apply present_day=2025.6.
"""
import json
import math
import sys

sys.path.insert(0, '/home/pyodide/app')

import numpy as np
from two_lambda.model import Variant, calibrate, simulate, thresholds, upstream_single_lambda

ANCHOR = 'uplift-solved'
DATES = {'native': None, 'legacy': 2025.6}
PLOT_START = 2024.0
_runs = {}


def _num(x):
    return None if x is None or not math.isfinite(float(x)) else float(x)


def _pack(result):
    times = np.asarray(result['times'], dtype=float)
    values = np.asarray(result['log10_E'], dtype=float)
    keep = np.flatnonzero((times >= PLOT_START) & np.isfinite(values))
    keep = keep[::2] if keep.size > 1200 else keep
    return {
        'milestones': {k: _num(v) for k, v in result['milestones'].items()},
        'takeoff_months': _num(result['takeoff_months']),
        'status': result['status'],
        'times': [round(float(t), 4) for t in times[keep]],
        'log10_E_eff': [round(float(v), 4) for v in values[keep]],
    }


def _cached(key, fn):
    if key not in _runs:
        _runs[key] = _pack(fn())
    return _runs[key]


def preset_info(preset):
    p = calibrate(ANCHOR, None, preset=preset).params
    return json.dumps({'lambda': p.parallel_penalty, 'ila': p.inf_labor_asymptote, 'beta': 1/p.r_software})


def run(preset, settings_json):
    s = json.loads(settings_json)
    dates = s.get('dates', 'native')
    if dates not in DATES:
        raise ValueError(f'Unknown dates setting {dates!r}')
    present_day = DATES[dates]
    preset_ila = calibrate(ANCHOR, None, preset=preset).params.inf_labor_asymptote
    ila = float(s['ila'])
    overrides = () if abs(ila/preset_ila - 1) < 1e-9 else (('inf_labor_asymptote', ila),)
    lam, eta = float(s['lambda']), s.get('eta', 'linear')
    model = calibrate(ANCHOR, present_day, preset=preset, overrides=overrides)
    common = dict(preset=preset, present_day=present_day, overrides=overrides)
    base = _cached((preset, dates, overrides, 'base'), lambda: simulate(Variant(model.params.parallel_penalty), ANCHOR, **common))
    base['thresholds'] = {k: float(v) for k, v in thresholds(model).items()}
    scenario = _pack(simulate(Variant(lam, eta), ANCHOR, **common))
    single = _cached((preset, dates, overrides, 'single', lam), lambda: upstream_single_lambda(lam, ANCHOR, **common))
    return json.dumps({'baseline': base, 'scenario': scenario, 'comparison': single})
