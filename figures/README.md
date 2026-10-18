# Figures: how λ moves the AI Futures Model's timelines

Scripts and data for the charts of how the coding labor parallelization penalty λ affects AC and ASI dates. Most charts are for the unmodified model (the `upstream/` submodule). The two-λ chart uses this repository's variant.

All runs are single deterministic runs at a preset's median parameters, at the preset's own present day (2026.578 for the 08/16/26 presets), not Monte Carlo forecasts.

## Regenerate

From the repository root, with the environment from the main README plus matplotlib:

```sh
python figures/make.py                  # redraw every figure from the committed data (seconds)
python figures/make.py lambda_takeoff   # one group only
python figures/make.py --rerun          # rerun the model first, then redraw (an hour or more)
```

The data files (`.csv`, `*_raw.json`) are committed, so redrawing needs no model runs. `--rerun` regenerates them. Rerunning `coding_uplift` and `lambda_sweep/sweep.py` reproduces the committed files exactly.

## Switching uses of λ one at a time

The model uses λ in several places, not only to turn parallel AI labor into serial labor. To split a λ change into its parts, `lambda_uses` and `lambda_takeoff` run a copy of upstream with [`lambda-sites.patch`](lambda-sites.patch) applied. The patch adds `progress_model/lamsite.py` and routes each use of λ through it, so each use can take its own value:

| Use | What it does with λ |
| --- | --- |
| `anchor` | Backs today's measured serial coding uplift out into today's automation level |
| `dynamics` | Converts growth in parallel coding labor after today into serial labor |
| `history` | Converts past human labor, which sets the r_software fit to 2024 software progress |
| `eta` | Rescales η from its λ = 0.5 estimate |
| `cap` | Converts the Maximum Serial Coding Labor Multiplier |

With no overrides the patched model gives upstream's results exactly. The bar charts give each use's Shapley value over every order of switching the uses from λ 0.5 to the new λ, and the whiskers show the effect when that use is switched first or last. The patched copy is built in `figures/.cache/` on first use; `upstream/` is not modified.

## The figures

**`lambda_sweep/`**: the unmodified model with λ varied from 0.3 to 1.
- `lambda-sweep-dates.png`: AC and ASI dates against λ, Daniel preset, at the preset's own present day. `lambda-sweep-durations.png` shows the same runs as time from today to AC and AC to ASI.
- `lambda-sweep-dates-presets.png`: the same for the Daniel, Eli and Brendan presets.
- `lambda-sweep-dates-anchors.png`: 3 presets × 3 AC anchors (Coding Uplift, Time Horizon, Revenue).
- `lambda-sweep-dates-anchors-low.png`: the same down to λ 0.03, under the model's η adjustment, the linear correction and no adjustment.
- `eta-adjustment-forms.png` and `lambda-eta-asi-shift.png`: η^(0.5/λ) against η·(0.5/λ), and how far the difference moves ASI.

**`coding_uplift/`**
- `coding-uplift-to-ac.png`: today's automated fraction and the path to AC when the Aug 2026 serial coding uplift is 1.5×, 2× or 3×.

**`lambda_uses/`**: the AC date split by use of λ.
- `lambda-uses-ac-0.65.png` and `lambda-uses-ac-1.png`: per-use shifts in the AC date for λ 0.5 → 0.65 and 0.5 → 1, for each AC anchor.
- `lambda-benefit-drag.png` and `lambda-benefit-dilution.png`: why the direct benefit of higher λ to AC is small (the CES bottleneck with human-only tasks, the labor asymptote, and when the extra labor arrives).

**`lambda_takeoff/`**: takeoff (AC to ASI) split by use of λ.
- `lambda-uses-takeoff-{0.65,1}.png` and `lambda-uses-asi-{0.65,1}.png`: per-use shifts in takeoff length and in the ASI date.
- `lambda-uses-takeoff-{0.65,1}-eta-split.png`: the same, with η's boost from higher λ and the η adjustment shown as separate bars. `-eta-net` shows them netted.
- `lambda-takeoff-asymptote.png`, `lambda-benefit-vs-asymptote.png`, `lambda-asymptote-takeoff-pct.png`, `lambda-asymptote-takeoff-bars.png`: the direct benefit of higher λ on takeoff at Infinite Coding Labor Asymptotes from 3× to effectively unbounded.
- `lambda-r-software.png` and `lambda-beta-software.png`: the r_software (= 1/β) refit against λ, shown as r and as β, and what the refit does to takeoff.
- `lambda-eta-adjustment.png`: takeoff against λ under the three η adjustments.

**`eta_issue/`**
- `eta-adjustment-issue.png`: η^(0.5/λ) against η·(0.5/λ) across λ, for η = 3 and for any η.

**`two_lambda_anchors/`**
- `lambda-sweep-dates-anchors-two-lambda.png`: the 3 × 3 anchor grid for the two-λ variant (η rescaled linearly), with the unmodified model's lines faint for comparison.
