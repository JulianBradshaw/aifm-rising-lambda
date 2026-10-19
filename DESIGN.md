# Design: a forward λ that rises over time

This repository is the [two-λ fixes](https://github.com/JulianBradshaw/aifm-lambda-fixes) plus a schedule for the forward λ. The fixes themselves are described in the [README](README.md).

## λ rising over time

The two-λ fixes give serial coding labor after the calibration date t0 as

    serial = norm · X0^λ_cal · (X / X0)^λ_f

with X parallel coding labor, X0 its value at t0, λ_cal = 0.5 the calibration λ and λ_f the forward λ. A schedule puts a time-varying λ(t) in place of λ_f:

    serial = norm · X0^λ_cal · (X / X0)^λ(t)

so a rise in λ raises the serial value of all growth in X since t0, the agents already running included, and not only of labor added after the rise. That is the usual reading of λ, a property of how well the whole workforce parallelizes, and better orchestration plausibly helps agents that are already deployed. Today's productivity is still pinned, since growth before t0 keeps λ_cal. The alternative, d ln(serial) = λ(t) · d ln X, applies each λ only to labor growth while it is in force; it needs one extra solver state and gives slightly longer takeoffs (by 0.2 to 0.4 months for the schedules in `outputs/RISING.md`).

A ramp changes serial labor gradually, by d ln(serial) = λ(t) · d ln X + λ'(t) · ln(X/X0) · dt; only an immediate step changes it at once, which is what a fixed λ_f from t0 already does. No extra solver state is needed. A flat schedule takes the original code path, and `tests/test_rising_lambda.py` checks that it reproduces the fixed forward λ exactly. The tests also check that a ramp beyond the horizon gives the same dates, that an immediate step equals the fixed λ it steps to, and that serial labor growth since t0 scales with λ(t) mid-ramp.

The schedule is `Variant(lambda_forward, lambda_end, ramp_start, ramp_years, ramp_shape)`: λ moves from lambda_forward at t0 to lambda_end over ramp_years starting at ramp_start (default t0), linearly or as the smoothstep 3x² − 2x³ used by the earlier swarm model's coordination ramp. The ramp ends are kinks in λ, so the solver restarts there.

**η.** η is rescaled for lambda_forward only, η · (λ_cal/lambda_forward), as in the fixed case. The rescale converts an η estimated under λ_cal into parallel-labor units for today's λ; a later rise in λ is better coordination of that labor, not a change in how much labor compute buys, so it should raise the serial value of η's growth too. Rescaling η for λ(t) at each moment would hold η's serial rate fixed, so the rise would act only on labor growth from human labor and inference compute. This is part of why the fast ramp to 1 gives a shorter takeoff than a fixed λ of 1, which is rescaled for 1. The other part is that takeoff is measured from AC, which the ramp reaches about two weeks later than a fixed λ of 1 does, so the ramp's takeoff is shorter even with η not rescaled, although its ASI also comes later.

**Serial cap.** The Maximum Serial Coding Labor Multiplier is applied exactly to the returned labor, (X_returned/H)^λ_cal ≤ M, at every λ; the CES frontier keeps the cap for lambda_forward.

**Not modeled.** λ before t0 stays at λ_cal: the rise from 0.5 to 0.65 that the evidence suggests between 2024 and today is not fed back into the calibration, which is the two-λ convention of pinning today's productivity. The schedule is exogenous in time; a λ that rises with capability rather than the calendar would need λ as a function of the progress state instead of t.
