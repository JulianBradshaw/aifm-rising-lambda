# Design: a forward λ that rises over time

This repository is the [two-λ fixes](https://github.com/JulianBradshaw/aifm-lambda-fixes) plus a schedule for the forward λ. The fixes themselves are described in the [README](README.md).

## λ rising over time

The two-λ fixes give serial coding labor after the calibration date t0 as

    serial = norm · X0^λ_cal · (X / X0)^λ_f

with X parallel coding labor, X0 its value at t0, λ_cal = 0.5 the calibration λ and λ_f the forward λ. Putting a time-varying λ(t) in place of λ_f would make a change in λ revalue all growth in X since t0 at once: a rise from 0.65 to 1 in 2028 would multiply serial labor by (X/X0)^0.35 overnight. A schedule for λ should instead mean that labor grows at the λ in force when it grows:

    d ln(serial) = λ(t) · d ln X

Integrating by parts from t0, with L = ln(X/X0),

    ln(serial / norm) = λ_cal ln X0 + λ(t) · L − W,     W(t) = ∫ λ'(τ) L(τ) dτ  from t0

so the solver carries one extra state, W, with dW/dt = λ'(t) · L. The derivative of X is never needed, and W stays 0 until λ starts to move, so with a flat schedule the formula is the fixed-λ one. A flat schedule does not even use the extra state: it takes the original code path, and `tests/test_rising_lambda.py` checks that it reproduces the fixed forward λ exactly. The tests also check that a ramp beyond the horizon runs the three-state solver to the same dates, that an immediate step equals the fixed λ it steps to, and that serial labor matches a direct quadrature of ∫ λ d ln X and not λ(t) · L.

The schedule is `Variant(lambda_forward, lambda_end, ramp_start, ramp_years, ramp_shape)`: λ moves from lambda_forward at t0 to lambda_end over ramp_years starting at ramp_start (default t0), linearly or as the smoothstep 3x² − 2x³ used by the earlier swarm model's coordination ramp. The ramp ends are kinks in λ, so the solver restarts there.

**η.** η is rescaled for lambda_forward only, η · (λ_cal/lambda_forward), as in the fixed case. The rescale converts an η estimated under λ_cal into parallel-labor units for today's λ; a later rise in λ is better coordination of that labor, not a change in how much labor compute buys, so it should raise the serial value of η's growth too. Rescaling η for λ(t) at each moment would need a second state of the same kind and would hold η's serial rate fixed, so the rise would act only on labor growth from human labor and inference compute. This is why the fast ramp to 1 gives a shorter takeoff than a fixed λ of 1, which is rescaled for 1.

**Serial cap.** The Maximum Serial Coding Labor Multiplier is applied exactly to the returned labor, (X_returned/H)^λ_cal ≤ M, at every λ; the CES frontier keeps the cap for lambda_forward.

**Not modeled.** λ before t0 stays at λ_cal: the rise from 0.5 to 0.65 that the evidence suggests between 2024 and today is not fed back into the calibration, which is the two-λ convention of pinning today's productivity. The schedule is exogenous in time; a λ that rises with capability rather than the calendar would need λ as a function of the progress state instead of t, which the same W state supports.
