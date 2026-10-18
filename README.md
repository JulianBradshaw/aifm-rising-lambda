# Two-λ AI Futures Model

A small variant of the public [AI Futures Model](https://github.com/AI-Futures-Project/aifm-public) that uses one parallelization penalty λ for the past and a separate one for the future. The upstream model is preserved unchanged in `upstream/` as a git submodule pinned to commit `1c40ecdb246c25980515441a66571931c5604e11` (MIT license in `upstream/LICENSE`); clone with `git clone --recurse-submodules`. This variant is MIT-licensed (`LICENSE`).

**[Run it in the browser](web/README.md)** · [results for the Daniel preset](outputs/REPORT.md) · [the same change as a patch to upstream](upstream-patch/) · [figures of how λ moves the model's timelines](figures/)

## Why two λs

λ converts parallel coding labor into serial labor: N times more parallel labor is worth N^λ times more serial labor. The AI Futures Model uses one λ for historical human teams and future AI swarms alike, so changing it does more than change how well swarms parallelize. Two calibrations of the past move with it:

1. **Reading today's coding uplift.** The model backs today's measured serial coding uplift (2× in August 2026 for the Daniel preset) out into an automation level. At higher λ the same 2× implies less parallel AI labor today, so the model starts from less automation and reaches the automated coder (AC) later.
2. **Refitting returns to software research.** r_software is scaled so that software efficiency grew 1.0 OOM a year in 2024. At higher λ, the growth in human researchers before 2024 explains more of that progress, so the fit lowers r_software (3.15 at λ 0.5, 2.86 at λ 1), which weakens the feedback loop during takeoff.

Both are side effects of using one λ for history and forecast. With the Coding Uplift anchor they outweigh the direct benefit: raising λ from 0.5 to 1 lengthens takeoff (AC to ASI) from 13.7 to 18.2 months.

## The variant

History and calibration keep the preset's λ (0.5). Today's automation fraction (60%), today's parallel AI labor (4.0× human) and r_software (3.146) are therefore the same at every forward λ. From the calibration date t0 on, a forward λ applies to growth in coding labor:

    serial coding labor = norm · X0^0.5 · (X / X0)^λ_forward      for t ≥ t0

where X is parallel coding labor and X0 its value at t0. Everything else is upstream's own code: the run is upstream's trajectory until t0, and after t0 upstream's rate function with this coding labor substituted.

Two further λ uses are adjusted for the forward λ:

- **η**, the coding automation efficiency improvement (OOMs per progress-year), was estimated at λ 0.5. It is rescaled linearly, η · (0.5/λ_forward), which keeps its serial-equivalent rate fixed. Upstream uses η^(0.5/λ), which is the conversion for a growth factor rather than a count of OOMs. Both, and no rescaling, are available as `eta_rescale='linear' | 'power' | 'none'`.
- The **Maximum Serial Coding Labor Multiplier** keeps its serial meaning: its parallel-labor cap is converted with the same mapping.

With the forward λ equal to the preset's, the variant returns upstream's trajectory exactly.

## Results

Daniel 08/16/26 preset, Coding Uplift anchor, native present day; single runs at preset medians, not forecasts.

| Takeoff, AC to ASI | λ 0.5 | λ 0.65 | λ 0.8 | λ 1 |
| --- | --- | --- | --- | --- |
| Two-λ, η linear (default) | 13.7 mo | 13.3 mo | 13.0 mo | 12.7 mo |
| Two-λ, η power | 13.7 mo | 13.3 mo | 12.8 mo | 12.3 mo |
| Two-λ, η not rescaled | 13.7 mo | 12.3 mo | 11.5 mo | 11.0 mo |
| Single λ (upstream) | 13.7 mo | 14.5 mo | 15.8 mo | 18.2 mo |

With two λs, higher λ shortens takeoff and brings AC slightly earlier (October to September 2027 at λ 1), instead of delaying AC by eight months. Most of the gap between the η rows is by design: the linear rescale holds η's serial rate fixed, so the forward λ adds nothing to the part of labor growth that comes from η. Whether that is right depends on how much of η's evidence measured faster serial work rather than cheaper copies; the "not rescaled" row is the other bound. The other anchors and presets are in [outputs/REPORT.md](outputs/REPORT.md); regenerate with `python -m two_lambda`.

## The same change as a patch to upstream

`upstream-patch/` makes the change directly in upstream's code instead of wrapping it, to show its size. Counting changed or added lines of Python, excluding comments:

| File | Change | Lines |
| --- | --- | --- |
| `1-calibration-lambda.diff` | New parameter `calibration_parallel_penalty` (0.5) | 1 |
| `2-uplift-backcalculation.diff` | Solve the automation schedule from today's uplift at the calibration λ | 3 |
| `3-history-refit.diff` | Historical labor, the r_software fit and the research-stock start at the calibration λ; forward λ for labor growth after today | 14 |
| `4-eta-linear.diff` | η · (0.5/λ) instead of η^(0.5/λ) | 1 |

The patched model agrees with this package to within a week on AC and ASI dates and 0.1 month on takeoff (`tests/test_upstream_patch.py`). The small differences come from the patch rescaling η for the whole run rather than only after today. Reported metrics that convert labor with λ (for example the serial coding labor multiplier) are not patched; they do not affect the trajectory.

## Run

Python 3.14 is recommended, matching upstream:

```sh
git clone --recurse-submodules https://github.com/JulianBradshaw/aifm-lambda-fixes
cd aifm-lambda-fixes
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m two_lambda      # writes outputs/REPORT.md and outputs/results.csv
.venv/bin/python -m pytest
```

On Windows, use `.venv\Scripts\python.exe`.

```python
from two_lambda.model import Variant, simulate, upstream_single_lambda

result = simulate(Variant(lambda_forward=1.0))  # eta_rescale='linear' by default
print(result['milestones'], result['takeoff_months'])
print(upstream_single_lambda(1.0)['takeoff_months'])  # the unmodified model at λ 1
```

`simulate` also takes `anchor` (`uplift-solved`, `time-horizon`, `revenue`, `eci`), `preset` (`daniel-08-16-26`, `eli-08-16-26`, `brendan-08-16-26`), `present_day` (None for the preset's own) and `overrides`, a tuple of (parameter, value) pairs passed to the calibration, such as `(('inf_labor_asymptote', 100),)`.

## Files

- `two_lambda/model.py`: calibration, the forward coding labor, milestones.
- `two_lambda/presets.py`: reads the pinned presets from `upstream/constants/parameters.ts`.
- `two_lambda/__main__.py`: the comparison report.
- `upstream-patch/`: the same change as diffs against `upstream/progress_model`.
- `tests/`: reproduction of upstream at λ 0.5, pinned calibration, the patch, and the browser entry point.
- `web/`: the browser page.
- `figures/`: scripts and data for the λ charts, for the unmodified model and the two-λ variant (`python figures/make.py`).
