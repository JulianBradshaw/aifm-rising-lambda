"""λ schedules: a flat schedule is the fixed forward λ, and a rise applies to all labor growth since today."""
import math
import numpy as np
import pytest
from two_lambda.model import Variant, simulate, calibrate, calibration_end, forward_params, interpolate
from progress_model import config as cfg


@pytest.fixture(scope='module')
def fixed():
    return simulate(Variant(0.65))


@pytest.fixture(scope='module')
def t0():
    return calibration_end(calibrate())


def test_flat_schedule_is_unchanged(fixed):
    for variant in (Variant(0.65, lambda_end=0.65), Variant(0.65, lambda_end=0.65, ramp_start=2028.0, ramp_shape='smoothstep')):
        result = simulate(variant)
        np.testing.assert_array_equal(result['log10_E'], fixed['log10_E'])
        assert result['milestones'] == fixed['milestones']
    # And at the preset's λ (the upstream path).
    assert simulate(Variant(0.5, lambda_end=0.5))['upstream_path']


def test_a_ramp_beyond_the_horizon_is_neutral(fixed):
    # A ramp beyond the horizon runs the time-varying λ path with λ constant; it must match the fixed run.
    result = simulate(Variant(0.65, lambda_end=1.0, ramp_start=2039.0), end=2035.0)
    for key in ('AC', 'ASI'):
        assert result['milestones'][key] == pytest.approx(fixed['milestones'][key], abs=1/365/24)


def test_an_immediate_step_matches_the_fixed_lambda_it_steps_to():
    # A step at the calibration date is the fixed forward λ, once η is not rescaled in either run.
    step = simulate(Variant(0.65, 'none', lambda_end=1.0, ramp_years=1e-4))
    flat = simulate(Variant(1.0, 'none'))
    for key in ('AC', 'ASI'):
        assert step['milestones'][key] == pytest.approx(flat['milestones'][key], abs=0.25/365)


def test_a_rise_revalues_all_labor_growth_since_today(t0):
    # ln(serial) - ln(serial at t0) must equal λ(t) ln(X/X0): a rise applies to the agents already running.
    model = calibrate()
    p, data = model.params, model.data
    times = np.asarray(model.results['times'])
    progress = np.asarray(model.results['progress'])
    variant = Variant(0.65, lambda_end=1.0, ramp_start=2027.5, ramp_years=1.0)
    labor = forward_params(model, variant, t0, float(np.interp(t0, times, progress))).automation_model
    t = 2028.0  # mid-ramp, before the serial cap binds
    lnE = math.log(cfg.BASE_FOR_SOFTWARE_LOM) * float(np.interp(t, times, progress))
    def serial_growth(lam):
        x = labor.at(lam).coding_labor_optimal_ces(interpolate(data, 'L_HUMAN', t), interpolate(data, 'inference_H100e', t), lnE, p)
        return p.parallel_penalty * math.log(float(x) / labor.x0)
    lam = variant.lambda_at(t, t0)
    assert 0.65 < lam < 1.0
    assert serial_growth(0.65) > 0.05
    assert serial_growth(lam) == pytest.approx(serial_growth(0.65) * lam / 0.65, rel=1e-9)


def test_rising_lambda_shortens_takeoff_but_barely_moves_ac(fixed):
    trend = simulate(Variant(0.65, lambda_end=1.0, ramp_years=4.86))
    ramp = simulate(Variant(0.65, lambda_end=1.0, ramp_start=2027.0, ramp_years=0.75, ramp_shape='smoothstep'))
    assert ramp['takeoff_months'] < trend['takeoff_months'] < fixed['takeoff_months']
    assert ramp['lambda_at']['ASI'] == 1.0
    for r in (trend, ramp):
        assert abs(r['milestones']['AC'] - fixed['milestones']['AC']) < 15/365
        assert r['calibration'] == fixed['calibration']


def test_invalid_schedules():
    with pytest.raises(ValueError):
        Variant(0.65, lambda_end=3.0)
    with pytest.raises(ValueError):
        Variant(0.65, lambda_end=1.0, ramp_years=0)
    with pytest.raises(ValueError):
        Variant(0.65, lambda_end=1.0, ramp_shape='step')
    with pytest.raises(ValueError):
        simulate(Variant(0.65, lambda_end=1.0, ramp_start=2025.0))
