"""Two-λ variant: one λ for history and calibration, a separate λ for coding labor from today on.

The AI Futures Model uses one parallelization penalty λ everywhere. Changing it therefore also
changes two calibrations that describe the past: reading today's serial coding uplift back into
an automation level, and fitting r_software to 2024 software progress. This variant keeps both
at the preset's λ (0.5), so today's automation fraction, AI labor and r_software do not move, and
applies a forward λ only to growth in coding labor after the calibration date:

    serial coding labor = norm * X0^lambda_cal * (X / X0)^lambda_forward   for t >= t0

X is parallel coding labor and X0 its value at t0. η (OOMs of coding efficiency per OOM of
effective compute) was estimated at λ = 0.5, so after t0 it is rescaled linearly,
η * (lambda_cal / lambda_forward), which keeps its serial-equivalent rate fixed. The upstream
model uses the power form η^(0.5/λ); both are offered for comparison. The Maximum Serial Coding
Labor Multiplier keeps its serial meaning: its parallel cap is converted with the same mapping.

No upstream files, global functions, or calibrated Parameters are mutated. With
lambda_forward equal to the preset's λ, the result is the upstream trajectory itself.
Milestones are dated where log10 effective compute crosses each threshold.

An optional λ schedule lets the forward λ rise after t0, from lambda_forward to lambda_end over
a ramp. λ(t) takes the place of lambda_forward in the formula above, so a rise applies to all
coding labor growth since t0, the agents already running included. With lambda_end unset or
equal to lambda_forward the run is the fixed forward λ above. See DESIGN.md.
"""
import copy
from dataclasses import dataclass, asdict
from functools import lru_cache
import logging
import math
import numpy as np
from scipy.integrate import solve_ivp
import hashlib
import json
from scipy.optimize import brentq
from . import UPSTREAM
from .presets import load_preset, ANCHORS
from progress_model import (Parameters, ProgressModel, load_time_series_data, compute_automation_fraction,
    compute_ai_research_taste)
from progress_model import config as cfg
from progress_model.progress_rate import progress_rate_at_time

ETA_RESCALES = ('linear', 'power', 'none')
RAMP_SHAPES = ('linear', 'smoothstep')


def interpolate(data, key, t):
    arr = getattr(data, key)
    return float(np.exp(np.interp(t, data.time, np.log(arr))))


def calibration_end(model):
    """The last date any historical anchor refers to; the forward λ applies from here."""
    p = model.params
    return max(float(getattr(p, key) or p.present_day) for key in
               ('present_day', 'uplift_reference_date', 'horizon_reference_date',
                'revenue_reference_date', 'eci_reference_date'))


def calibration_snapshot(model):
    """Calibrated quantities a forward run must not change."""
    p = model.params
    snapshot = {'r_software': p.r_software, 'ac_progress': p.progress_at_aa, 'taste_slope': p.ai_research_taste_slope,
                'automation_anchors': p.automation_anchors, 'automation_efficiency_slope': p.coding_automation_efficiency_slope,
                'lambda': p.parallel_penalty, 'ila': p.inf_labor_asymptote,
                'ces': [p.rho_experiment_capacity, p.alpha_experiment_capacity, p.experiment_compute_exponent]}
    snapshot['sha256'] = hashlib.sha256(json.dumps(snapshot, sort_keys=True, default=str).encode()).hexdigest()
    return snapshot


def thresholds(model):
    """log10 effective-compute thresholds for AC, SAR, TED-AI and ASI."""
    p = model.params
    result = {'AC': p.progress_at_aa}
    for label, key in [('SAR', 'SAR-level-experiment-selection-skill'), ('TED-AI', 'TED-AI'), ('ASI', 'ASI')]:
        target = model.results['milestones'][key]['target']
        def residual(e):
            return p.taste_distribution.get_sd_of_taste(compute_ai_research_taste(e, p)) - target
        result[label] = max(p.progress_at_aa if label == 'SAR' else -np.inf,
                            brentq(residual, p.progress_at_aa-20, p.progress_at_aa+60))
    return result


def crossing(times, values, target):
    """First time values reach target, interpolated linearly; None if never."""
    idx = np.flatnonzero(np.isfinite(values) & (values >= target))
    if not idx.size:
        return None
    j = int(idx[0])
    if j == 0:
        return float(times[0])
    return float(times[j-1] + (times[j]-times[j-1])*(target-values[j-1])/(values[j]-values[j-1]))


@dataclass(frozen=True)
class Variant:
    """Forward settings. lambda_forward applies to coding labor growth after the calibration date.

    eta_rescale sets how η is adjusted for lambda_forward after that date: 'linear' is
    η * (λ_cal/λ_forward), 'power' is upstream's η^(λ_cal/λ_forward), 'none' keeps η.

    lambda_end sets a λ schedule: λ moves from lambda_forward to lambda_end over ramp_years
    starting at ramp_start (None means the calibration date), linearly or as a smoothstep.
    lambda_forward stays the λ at the calibration date, and η is rescaled for it alone.
    """
    lambda_forward: float = 0.5
    eta_rescale: str = 'linear'
    lambda_end: float | None = None
    ramp_start: float | None = None
    ramp_years: float = 1.0
    ramp_shape: str = 'linear'

    def __post_init__(self):
        if not math.isfinite(self.lambda_forward) or not 0.05 <= self.lambda_forward <= 2:
            raise ValueError('lambda_forward must be in [0.05, 2]')
        if self.eta_rescale not in ETA_RESCALES:
            raise ValueError(f'eta_rescale must be one of {ETA_RESCALES}')
        if self.lambda_end is not None and (not math.isfinite(self.lambda_end) or not 0.05 <= self.lambda_end <= 2):
            raise ValueError('lambda_end must be in [0.05, 2]')
        if not math.isfinite(self.ramp_years) or self.ramp_years <= 0:
            raise ValueError('ramp_years must be positive')
        if self.ramp_start is not None and not math.isfinite(self.ramp_start):
            raise ValueError('ramp_start must be finite')
        if self.ramp_shape not in RAMP_SHAPES:
            raise ValueError(f'ramp_shape must be one of {RAMP_SHAPES}')

    @property
    def rising(self):
        """True when λ changes after the calibration date."""
        return self.lambda_end is not None and self.lambda_end != self.lambda_forward

    def ramp_window(self, t0):
        start = t0 if self.ramp_start is None else self.ramp_start
        return start, start + self.ramp_years

    def lambda_at(self, t, t0):
        """Forward λ at time t (t0 is the calibration date)."""
        if not self.rising:
            return self.lambda_forward
        start, stop = self.ramp_window(t0)
        x = min(max((t - start) / self.ramp_years, 0.0), 1.0)
        q = x if self.ramp_shape == 'linear' else x*x*(3 - 2*x)
        return self.lambda_forward + (self.lambda_end - self.lambda_forward) * q

    def eta_factor(self, eta, lambda_cal):
        """Forward η divided by calibrated η; eta is the input value in OOMs per progress-year."""
        ratio = lambda_cal / self.lambda_forward
        return {'linear': ratio, 'power': eta**(ratio-1), 'none': 1.0}[self.eta_rescale]


@lru_cache(maxsize=24)
def calibrate(anchor='uplift-solved', present_day=None, *, preset='daniel-08-16-26', overrides=()):
    """Upstream calibration of a preset; overrides is a tuple of (parameter, value) pairs."""
    if anchor not in ANCHORS:
        raise ValueError(f'Unknown AC anchor: {anchor}')
    values = load_preset(preset) | dict(overrides)
    values['ac_anchor_mode'] = anchor
    if present_day is not None:
        values['present_day'] = present_day
    previous_logging_disable = logging.root.manager.disable
    logging.disable(logging.WARNING)
    try:
        model = ProgressModel(Parameters(**values), load_time_series_data(str(UPSTREAM / 'inputs/input_data.csv')))
        model.compute_progress_trajectory([2017, 2040], rebase_output=False)
    finally:
        logging.disable(previous_logging_disable)
    return model


class ForwardLabor:
    """Stands in for the calibrated AutomationModel after t0.

    Returns the parallel labor that, raised to lambda_cal by upstream's rate function, gives
    X0^lambda_cal * (X/X0)^lambda_forward. The forward η stretches the effective-compute axis
    above t0's progress by eta_factor, which leaves which tasks are automated unchanged and
    multiplies every task's efficiency growth after t0 by the same factor.

    With a λ schedule, λ(t) replaces lambda_forward: X0 (X/X0)^(λ(t)/lambda_cal), so better
    coordination raises the serial value of all labor growth since t0, not only of growth after
    the rise. at(lam) sets the λ for the next call.
    """
    def __init__(self, params, variant, eta, progress0, human0, inference0):
        self.base, self.lambda_cal = params.automation_model, params.parallel_penalty
        self.exponent = variant.lambda_forward / self.lambda_cal
        self.rising, self.lam = variant.rising, variant.lambda_forward
        self.k = variant.eta_factor(eta, self.lambda_cal)
        self.ln0 = math.log(cfg.BASE_FOR_SOFTWARE_LOM) * progress0
        self.x0 = self.base.coding_labor_optimal_ces(human0, inference0, self.ln0, params)
        self.forward = copy.copy(self.base)
        self.forward._frontier_pc = self.forward._frontier_params_signature = None
        progress_from_index = self.base.get_progress_from_index
        self.forward.get_progress_from_index = lambda index: self.stretch(progress_from_index(index), progress0)
        self.params = copy.copy(params)
        # The serial cap M means serial labor / human serial labor <= M, that is
        # (returned X / H)^lambda_cal <= M. Upstream builds it into the frontier as X/H <= M^(1/lambda_cal).
        # The forward frontier gets the cap that matches at t0, n0 * (M / n0^lambda_cal)^(1/lambda_forward)
        # with n0 = X0/H0, and since that drifts as H grows, the returned labor is also capped exactly.
        n0 = self.x0 / human0
        cap = params.max_serial_coding_labor_multiplier
        # At lambda_forward == lambda_cal the frontier cap is upstream's own and does not drift.
        # With a λ schedule the frontier keeps the cap for lambda_forward and the exact cap does the rest.
        self.max_parallel_per_human = (None if cap is None or (self.exponent == 1 and not self.rising)
                                       else cap**(1/self.lambda_cal))
        if cap is not None:
            self.params.optimal_ces_frontier_cap = float(np.clip(
                n0 * (cap / n0**self.lambda_cal)**(1/variant.lambda_forward), *cfg.PARAMETER_BOUNDS['optimal_ces_frontier_cap']))
        self.xf0 = self.forward.coding_labor_optimal_ces(human0, inference0, self.ln0, self.params)
        if not all(np.isfinite([self.x0, self.xf0])) or min(self.x0, self.xf0) <= 0:
            raise FloatingPointError('Invalid coding labor at the calibration date')

    def at(self, lam):
        self.lam = lam
        return self

    def stretch(self, x, x0):
        return np.where(x > x0, x0 + self.k*(x - x0), x)

    def coding_labor_optimal_ces(self, H, C, logE, params, return_details=False):
        x = self.forward.coding_labor_optimal_ces(H, C, self.stretch(logE, self.ln0), self.params)
        if x is None or not np.all(np.isfinite(x)):
            raise FloatingPointError('Forward coding labor failed')
        x = self.x0 * (x / self.xf0)**(self.lam / self.lambda_cal if self.rising else self.exponent)
        return x if self.max_parallel_per_human is None else np.minimum(x, H * self.max_parallel_per_human)

    def __getattr__(self, name):
        return getattr(self.base, name)


def eta_input(model):
    """The calibrated η in input units (OOMs per progress-year), before upstream converts it per progress unit."""
    return model._original_automation_efficiency_slope


def forward_params(model, variant, t0, progress0):
    """A shallow copy of the calibrated Parameters whose automation model is ForwardLabor."""
    p, data = model.params, model.data
    params = copy.copy(p)
    params.automation_model = ForwardLabor(p, variant, eta_input(model), progress0,
        interpolate(data, 'L_HUMAN', t0), interpolate(data, 'inference_H100e', t0))
    return params


def simulate(variant=None, anchor='uplift-solved', end=2040.0, max_step=1/24, *,
             preset='daniel-08-16-26', present_day=None, overrides=(), force_ode=False):
    """Milestones for one forward λ. overrides are passed to the calibration (see calibrate).

    force_ode integrates even when the variant equals upstream, for the reproduction check.
    """
    variant = variant if variant is not None else Variant()
    model = calibrate(anchor, present_day, preset=preset, overrides=tuple(overrides))
    p, data = model.params, model.data
    if p.coding_labor_mode != 'optimal_ces':
        raise ValueError('The two-λ variant needs the optimal_ces coding labor mode')
    t0 = calibration_end(model)
    if not t0 < end <= 2040 or not math.isfinite(max_step) or max_step <= 0:
        raise ValueError('end must be after calibration and no later than 2040; step must be positive')
    before = calibration_snapshot(model)
    targets = thresholds(model)
    rs0 = float(model.results['research_stock'][0])
    eta = eta_input(model)
    unchanged = (not force_ode and variant.lambda_forward == p.parallel_penalty and not variant.rising
                 and variant.eta_factor(eta, p.parallel_penalty) == 1)
    if variant.rising and variant.ramp_window(t0)[0] < t0:
        raise ValueError('the λ ramp cannot start before the calibration date')
    status, solved_until, forward, segments = 'complete', end, None, []
    if unchanged:
        full_times = np.asarray(model.results['times'])
        keep = full_times <= end
        times = full_times[keep]
        raw = np.asarray(model.results['progress'])[keep].copy()
        stock = np.asarray(model.results['research_stock'])[keep].copy()
        if times[-1] < end <= full_times[-1]:
            times = np.r_[times, end]
            raw = np.r_[raw, np.interp(end, full_times, model.results['progress'])]
            stock = np.r_[stock, np.interp(end, full_times, model.results['research_stock'])]
    else:
        times = np.unique(np.r_[np.linspace(2017, end, int((end-2017)*120)+1), t0])
        raw, stock = np.full(len(times), np.nan), np.full(len(times), np.nan)
        ceiling = max(targets.values()) + 10
        def ceiling_event(t, y):
            return y[0]-ceiling
        ceiling_event.terminal, ceiling_event.direction = True, 1
        state = [model.results['progress'][0], rs0]
        # The ramp's ends are kinks in λ, so the solver restarts there.
        breaks = [x for x in variant.ramp_window(t0) if variant.rising and t0 < x < end]
        bounds = [2017., t0, *breaks, end]
        for a, b in zip(bounds[:-1], bounds[1:]):
            if a == t0:
                forward = forward_params(model, variant, t0, float(state[0]))
            params = p if forward is None else forward
            if forward is None or not variant.rising:
                rhs = lambda t, y: progress_rate_at_time(t, y, data, params, RS_0=rs0)
            else:
                def rhs(t, y, params=params):
                    params.automation_model.at(variant.lambda_at(t, t0))
                    return progress_rate_at_time(t, y, data, params, RS_0=rs0)
            sol = solve_ivp(rhs, [a, b], state, method='Radau', rtol=1e-6, atol=1e-8,
                            max_step=max_step, dense_output=True, events=ceiling_event)
            if not sol.success:
                raise RuntimeError(sol.message)
            segments.append((a, float(sol.t[-1]), sol.sol))
            mask = (times >= a) & (times <= sol.t[-1])
            raw[mask], stock[mask] = sol.sol(times[mask])
            state = sol.y[:,-1].copy()
            if sol.status == 1:
                status, solved_until = 'capability_ceiling', float(sol.t[-1])
                last = times[mask][-1] if mask.any() else a
                extra = np.linspace(last, solved_until, 201)[1:]
                at = np.searchsorted(times, extra)
                values = sol.sol(extra)
                times, raw, stock = np.insert(times, at, extra), np.insert(raw, at, values[0]), np.insert(stock, at, values[1])
                break
    milestones = {k: crossing(times, raw, v) for k, v in targets.items()}
    def progress_at(t):
        """log10_E at t from the solver's dense output."""
        for a, b, dense in segments:
            if a <= t <= b:
                return dense(t)[0]
        return np.interp(t, times, raw)
    if segments:
        # Grid crossings only bracket each milestone; locate it on the continuous solution, since
        # during a fast takeoff the state can move by orders of magnitude between grid points.
        for k, target in targets.items():
            m = milestones[k]
            if m is None or m <= times[0]:
                continue
            j = int(np.searchsorted(times, m))
            lo, hi = times[max(j-1, 0)], times[min(j, len(times)-1)]
            if lo < hi and progress_at(lo) < target <= progress_at(hi):
                milestones[k] = float(brentq(lambda t: progress_at(t) - target, lo, hi, xtol=1e-10))
    if calibration_snapshot(model) != before:
        raise AssertionError('Calibration was mutated during simulation')
    progress0 = float(np.interp(t0, times, raw))
    labor = forward.automation_model if forward is not None else None
    return {'variant': asdict(variant), 'anchor': anchor, 'preset': preset, 'present_day': p.present_day,
        'overrides': dict(overrides), 'calibration_end': t0, 'calibration': before, 'thresholds': targets,
        'milestones': milestones, 'upstream_path': bool(unchanged),
        'takeoff_months': 12*(milestones['ASI']-milestones['AC']) if None not in (milestones['ASI'], milestones['AC']) else None,
        'lambda_calibration': p.parallel_penalty, 'r_software': p.r_software,
        'automation_fraction_t0': compute_automation_fraction(progress0, p),
        'parallel_labor_per_human_t0': (labor.x0 if labor else p.automation_model.coding_labor_optimal_ces(
            interpolate(data, 'L_HUMAN', t0), interpolate(data, 'inference_H100e', t0),
            math.log(cfg.BASE_FOR_SOFTWARE_LOM)*progress0, p)) / interpolate(data, 'L_HUMAN', t0),
        'eta_calibration': eta, 'eta_forward': eta*variant.eta_factor(eta, p.parallel_penalty),
        'lambda_at': {k: variant.lambda_at(m, t0) for k, m in milestones.items() if m is not None},
        'status': status, 'solved_until': solved_until, 'times': times, 'log10_E': raw, 'research_stock': stock}


def upstream_single_lambda(lam, anchor='uplift-solved', *, preset='daniel-08-16-26', present_day=None, overrides=()):
    """The unmodified model with one λ everywhere, dated the same way, for comparison."""
    overrides = tuple(dict(overrides, parallel_penalty=lam).items())
    return simulate(Variant(lambda_forward=lam, eta_rescale='linear'), anchor,
                    preset=preset, present_day=present_day, overrides=overrides)
