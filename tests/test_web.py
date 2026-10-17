"""The browser page's Python entry point must give the same answers as the model API."""
import importlib.util
import json
from pathlib import Path
import pytest
from two_lambda.model import Variant, simulate, upstream_single_lambda

RUNNER = Path(__file__).resolve().parents[1] / 'web' / 'runner.py'


@pytest.fixture(scope='module')
def runner():
    spec = importlib.util.spec_from_file_location('web_runner', RUNNER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_runner_matches_model(runner):
    out = json.loads(runner.run('daniel-08-16-26', json.dumps({'lambda': 1, 'ila': 15, 'eta': 'linear'})))
    expected = {'baseline': simulate(), 'scenario': simulate(Variant(1)), 'comparison': upstream_single_lambda(1)}
    for name, direct in expected.items():
        for key in ('AC', 'ASI'):
            assert out[name]['milestones'][key] == pytest.approx(direct['milestones'][key], abs=1e-9)
        assert out[name]['takeoff_months'] == pytest.approx(direct['takeoff_months'], abs=1e-6)
    assert set(out['baseline']['thresholds']) == {'AC', 'SAR', 'TED-AI', 'ASI'}


def test_runner_asymptote_and_eta(runner):
    out = json.loads(runner.run('daniel-08-16-26', json.dumps({'lambda': 0.65, 'ila': 100, 'eta': 'none', 'dates': 'legacy'})))
    common = dict(present_day=2025.6, overrides=(('inf_labor_asymptote', 100.0),))
    assert out['scenario']['takeoff_months'] == pytest.approx(simulate(Variant(0.65, 'none'), **common)['takeoff_months'], abs=1e-6)
    assert out['baseline']['takeoff_months'] == pytest.approx(simulate(**common)['takeoff_months'], abs=1e-6)
