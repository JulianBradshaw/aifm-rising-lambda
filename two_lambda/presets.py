"""Explicit UI-to-model conversion for the three pinned August 2026 presets (from upstream/constants/parameters.ts).

Only literal-valued preset blocks are accepted. We do not evaluate TypeScript.
Unsupported/unknown fields fail, except the documented display-only fields.
"""
from dataclasses import fields
import json
import re
from . import UPSTREAM
from progress_model import Parameters

PRESETS = ('daniel-08-16-26', 'eli-08-16-26', 'brendan-08-16-26')
ANCHORS = ('uplift-solved', 'time-horizon', 'revenue', 'eci')
DISPLAY_ONLY = {'swe_multiplier_at_present_day', 'constant_training_system_performance_growth_rate',
                'slowdown_year', 'post_slowdown_training_system_performance_growth_rate'}


def load_preset(name):
    if name not in PRESETS:
        raise ValueError(f'Unknown preset {name!r}; expected one of {PRESETS}')
    source = (UPSTREAM / 'constants/parameters.ts').read_text(encoding='utf-8')
    marker = f"'{name}': {{"
    if source.count(marker) != 1:
        raise ValueError(f'Expected one literal block for {name}')
    block = source.split(marker, 1)[1].split('} as ParametersType', 1)[0]
    values = {}
    for line in block.splitlines():
        line = line.split('//', 1)[0].strip().rstrip(',')
        if not line:
            continue
        match = re.fullmatch(r'(\w+):\s*(.+)', line)
        if not match:
            raise ValueError(f'Unsupported preset syntax: {line}')
        key, literal = match.groups()
        if key in values:
            raise ValueError(f'Duplicate preset key: {key}')
        values[key] = json.loads(literal.replace("'", '"'))
    values['parallel_penalty'] = values.pop('coding_labor_exponent')
    values['ac_time_horizon_minutes'] = 10 ** values['ac_time_horizon_minutes']
    values['include_gap'] = 'gap' if values.pop('benchmarks_and_gaps_mode') else 'no gap'
    allowed = {f.name for f in fields(Parameters) if f.init}
    unknown = set(values) - allowed - DISPLAY_ONLY
    if unknown:
        raise ValueError(f'Unmapped preset fields: {sorted(unknown)}')
    return {k: v for k, v in values.items() if k in allowed}

