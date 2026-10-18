import math
import numpy as np
import pytest
from two_lambda.model import Variant, simulate, calibrate, forward_params, upstream_single_lambda, interpolate
from progress_model import config as cfg
from progress_model.progress_rate import progress_rate_at_time


@pytest.fixture(scope='module')
def baseline():
    return simulate()


@pytest.fixture(scope='module')
def forced():
    return simulate(force_ode=True)


def test_preset_lambda_is_the_upstream_trajectory(baseline):
    assert baseline['upstream_path'] and baseline['lambda_calibration'] == 0.5
    model = calibrate()
    keep = np.asarray(model.results['times']) <= 2040
    np.testing.assert_array_equal(baseline['log10_E'][:keep.sum()], np.asarray(model.results['progress'])[keep])
    # Same trajectory; upstream's own milestone dates differ from threshold crossings by about a day.
    for k, key in [('AC', 'AC'), ('SAR', 'SAR-level-experiment-selection-skill'), ('TED-AI', 'TED-AI'), ('ASI', 'ASI')]:
        assert abs(baseline['milestones'][k] - model.results['milestones'][key]['time'])*365.25 < 2
    assert baseline['takeoff_months'] == pytest.approx(13.67, abs=0.01)


def test_forward_labor_is_the_identity_at_the_preset_lambda():
    model = calibrate()
    p, data = model.params, model.data
    t0 = model.params.present_day
    progress0 = float(np.interp(t0, model.results['times'], model.results['progress']))
    forward = forward_params(model, Variant(0.5), t0, progress0)
    rs0 = float(model.results['research_stock'][0])
    for t in [t0, 2027.5, 2028.5, 2029.5]:
        y = [float(np.interp(t, model.results['times'], model.results[k])) for k in ('progress', 'research_stock')]
        lnE = math.log(cfg.BASE_FOR_SOFTWARE_LOM)*y[0]
        h, c = interpolate(data, 'L_HUMAN', t), interpolate(data, 'inference_H100e', t)
        assert forward.automation_model.coding_labor_optimal_ces(h, c, lnE, forward) == pytest.approx(
            p.automation_model.coding_labor_optimal_ces(h, c, lnE, p), rel=1e-12)
        np.testing.assert_allclose(progress_rate_at_time(t, y, data, forward, RS_0=rs0),
                                   progress_rate_at_time(t, y, data, p, RS_0=rs0), rtol=1e-12)


def test_forced_integration_reproduces_upstream_dates(baseline, forced):
    assert not forced['upstream_path']
    for k, date in baseline['milestones'].items():
        assert abs(forced['milestones'][k] - date)*365.25 < 2  # ODE solver differences


@pytest.mark.parametrize('lam', [0.65, 1.0])
def test_calibration_and_history_do_not_move(forced, lam):
    result = simulate(Variant(lam))
    assert result['calibration'] == forced['calibration']
    for key in ('r_software', 'automation_fraction_t0', 'parallel_labor_per_human_t0'):
        assert result[key] == forced[key]
    before = result['times'] <= result['calibration_end']
    np.testing.assert_array_equal(result['log10_E'][before], forced['log10_E'][before])


def test_linear_eta_keeps_the_serial_rate():
    for lam in [0.3, 0.65, 1.0]:
        result = simulate(Variant(lam))
        assert lam*result['eta_forward'] == pytest.approx(0.5*result['eta_calibration'], rel=1e-12)
    assert simulate(Variant(1.0, 'power'))['eta_forward'] == pytest.approx(simulate()['eta_calibration']**0.5)


def test_higher_forward_lambda_shortens_takeoff(baseline):
    takeoff = [simulate(Variant(lam))['takeoff_months'] for lam in [0.65, 1.0]]
    assert baseline['takeoff_months'] > takeoff[0] > takeoff[1]
    # Without the η rescale the benefit is larger; upstream's single λ lengthens takeoff instead.
    assert simulate(Variant(1.0, 'none'))['takeoff_months'] < takeoff[1]
    assert upstream_single_lambda(1.0)['takeoff_months'] > baseline['takeoff_months']


def test_invalid_settings():
    with pytest.raises(ValueError):
        Variant(0)
    with pytest.raises(ValueError):
        Variant(1, 'quadratic')


def test_serial_cap_holds_as_human_labor_grows():
    model = calibrate()
    p, t0 = model.params, model.params.present_day
    progress0 = float(np.interp(t0, model.results['times'], model.results['progress']))
    labor = forward_params(model, Variant(1.0), t0, progress0).automation_model
    for t in (t0, 2028.0, 2030.0):
        h, c = interpolate(model.data, 'L_HUMAN', t), interpolate(model.data, 'inference_H100e', t)
        x = labor.coding_labor_optimal_ces(h, c, math.log(10)*80, p)
        assert (x / h)**p.parallel_penalty <= p.max_serial_coding_labor_multiplier * (1 + 1e-9)

