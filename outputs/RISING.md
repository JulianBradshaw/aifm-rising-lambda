# λ rising over time (daniel-08-16-26, uplift-solved anchor)

History and calibration keep λ 0.5. From the calibration date (2026.58) the forward λ starts at 0.65 and follows each schedule; serial coding labor grows as λ(t) times the growth of parallel labor, so a later rise applies only to growth after it. η is rescaled for today's λ (0.5/0.65) and not for the later rise. Takeoff is AC to ASI; deterministic single runs at preset medians, not forecasts. Regenerate with `python -m two_lambda.rising_sweep`.

| Schedule | λ at AC | λ at ASI | AC | ASI | Takeoff |
| --- | --- | --- | --- | --- | --- |
| Fixed λ 0.5 | 0.50 | 0.50 | 2027-10 | 2028-12 | 13.7 mo |
| Flat at 0.65 from today | 0.65 | 0.65 | 2027-10 | 2028-11 | 13.3 mo |
| 2024–26 trend (+0.072/yr), capped at 1 | 0.73 | 0.81 | 2027-09 | 2028-10 | 12.6 mo |
| Ramp to 1 over 2027 (aifm-swarm shape) | 1.00 | 1.00 | 2027-09 | 2028-09 | 11.6 mo |
| Fixed λ 1 from today | 1.00 | 1.00 | 2027-09 | 2028-09 | 12.7 mo |

With η not rescaled at all (the other bound used in the two-λ results):

| Schedule | λ at AC | λ at ASI | AC | ASI | Takeoff |
| --- | --- | --- | --- | --- | --- |
| Fixed λ 0.5 | 0.50 | 0.50 | 2027-10 | 2028-12 | 13.7 mo |
| Flat at 0.65 from today | 0.65 | 0.65 | 2027-09 | 2028-10 | 12.3 mo |
| 2024–26 trend (+0.072/yr), capped at 1 | 0.73 | 0.80 | 2027-09 | 2028-09 | 11.8 mo |
| Ramp to 1 over 2027 (aifm-swarm shape) | 1.00 | 1.00 | 2027-09 | 2028-08 | 11.0 mo |
| Fixed λ 1 from today | 1.00 | 1.00 | 2027-09 | 2028-07 | 11.0 mo |

![λ schedules and AC to ASI for each](rising-lambda.png)
