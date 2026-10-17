"""upstream-patch/ edits the upstream code directly; it should agree with the two_lambda wrapper."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import pytest
from two_lambda.model import Variant, simulate

ROOT = Path(__file__).resolve().parents[1]

SCRIPT = '''
import json, logging, sys
import numpy as np
sys.path.insert(0, sys.argv[1])
from progress_model import Parameters, ProgressModel, load_time_series_data
sys.path.insert(1, sys.argv[2])
from two_lambda import UPSTREAM
from two_lambda.presets import load_preset
from two_lambda.model import thresholds, crossing
logging.disable(logging.WARNING)
out = {}
for lam in (0.5, 0.65, 1.0):
    values = load_preset('daniel-08-16-26') | {'ac_anchor_mode': 'uplift-solved', 'parallel_penalty': lam}
    model = ProgressModel(Parameters(**values), load_time_series_data(str(UPSTREAM / 'inputs/input_data.csv')))
    model.compute_progress_trajectory([2017, 2040], rebase_output=False)
    t, p = np.asarray(model.results['times']), np.asarray(model.results['progress'])
    m = {k: crossing(t, p, v) for k, v in thresholds(model).items()}
    out[lam] = {'AC': m['AC'], 'ASI': m['ASI'], 'r_software': model.params.r_software}
print(json.dumps(out))
'''


@pytest.fixture(scope='module')
def patched(tmp_path_factory):
    work = tmp_path_factory.mktemp('patched')
    shutil.copytree(ROOT/'upstream/progress_model', work/'progress_model')
    for diff in sorted((ROOT/'upstream-patch').glob('*.diff')):
        subprocess.run(['git', 'apply', str(diff)], cwd=work, check=True)
    result = subprocess.run([sys.executable, '-c', SCRIPT, str(work), str(ROOT)], check=True, capture_output=True, text=True)
    return {float(k): v for k, v in json.loads(result.stdout.splitlines()[-1]).items()}


def test_patch_reproduces_upstream_at_the_preset_lambda(patched):
    base = simulate()
    assert patched[0.5]['AC'] == pytest.approx(base['milestones']['AC'], abs=1e-9)
    assert patched[0.5]['ASI'] == pytest.approx(base['milestones']['ASI'], abs=1e-9)


@pytest.mark.parametrize('lam', [0.65, 1.0])
def test_patch_matches_the_wrapper(patched, lam):
    # The patch rescales η over the whole run and converts the serial cap with the forward λ alone;
    # the wrapper does both only from today on. Dates agree within about a week, takeoff within days.
    wrapper = simulate(Variant(lam))
    assert patched[lam]['r_software'] == pytest.approx(wrapper['r_software'], rel=1e-9)
    for k in ('AC', 'ASI'):
        assert abs(patched[lam][k] - wrapper['milestones'][k])*12 < 0.25
    takeoff = 12*(patched[lam]['ASI'] - patched[lam]['AC'])
    assert takeoff == pytest.approx(wrapper['takeoff_months'], abs=0.1)
