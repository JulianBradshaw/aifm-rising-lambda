# Runs the unmodified AI Futures Model (the pinned upstream/ submodule) through its own
# API, with presets read from upstream's constants/parameters.ts the way the site reads them.
import re, sys, os, logging
ROOT = os.path.abspath(os.environ.get('AIFM_ROOT', os.path.join(os.path.dirname(__file__), '..', 'upstream')))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'api'))
logging.disable(logging.CRITICAL)
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    from api.index import app

def preset(name):
    src = open(os.path.join(ROOT, 'constants/parameters.ts'), encoding='utf-8').read()
    i = src.index(f"'{name}': {{"); j = src.index('} as ParametersType', i)
    d = {}
    for line in src[i:j].splitlines()[1:]:
        line = line.split('//')[0].strip().rstrip(',')
        m = re.match(r"(\w+):\s*(.+)$", line)
        if not m: continue
        k, v = m.groups()
        if v == 'null': v = None
        elif v in ('true', 'false'): v = (v == 'true')
        elif v.startswith("'"): v = v.strip("'")
        else: v = float(v)
        d[k] = v
    # site conversion (utils/monteCarlo.ts convertParametersToAPIFormat)
    d['ac_time_horizon_minutes'] = 10 ** d['ac_time_horizon_minutes']
    if d.get('serial_uplift_at_reference_date') is not None: d.pop('swe_multiplier_at_present_day', None)
    if 'benchmarks_and_gaps_mode' in d:
        d['include_gap'] = 'gap' if d.pop('benchmarks_and_gaps_mode') in (True, 'gap') else 'no gap'
    d['parallel_penalty'] = d.pop('coding_labor_exponent')
    return {k: v for k, v in d.items() if v is not None or k in ('swe_multiplier_at_present_day',)}

client = app.test_client()
def run(p):
    """AC and ASI dates (decimal years) for a parameter dict, or (None, None, error)."""
    with contextlib.redirect_stdout(io.StringIO()):
        r = client.post('/api/compute', json={'parameters': p, 'time_range': [2017, 2200], 'initial_progress': 0.0})
    js = r.get_json()
    if r.status_code != 200: return None, None, js
    ms = js['milestones']
    return ms.get('AC', {}).get('time'), ms.get('ASI', {}).get('time'), None
