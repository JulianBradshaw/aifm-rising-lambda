# Browser version

A static page that runs `two_lambda` in the browser with [Pyodide](https://pyodide.org) (Python compiled to WebAssembly). There is no server: the page downloads Pyodide, numpy and scipy from the jsDelivr CDN (about 30 MB, cached after the first visit), unpacks the model sources from `model.zip`, and solves each setting in a Web Worker.

Each setting runs three times: the preset at its own λ (dashed), the two-λ variant at the chosen forward λ and λ schedule (solid), and the original model with that λ everywhere (dotted). Changing the forward λ or the λ schedule re-solves only the variant and, the first time each λ is used, the single-λ model; changing the labor asymptote recalibrates all three.

- `index.html`, `style.css`, `app.js`: the page, sliders and SVG charts (no build step, no chart library).
- `worker.js`: loads Pyodide and runs the model off the main thread.
- `runner.py`: the Python entry point; calls `two_lambda.model` with the page's settings.
- `bundle.py`: writes `model.zip` from `two_lambda/` and the pinned upstream files it needs.

## Run locally

```sh
git submodule update --init
python web/bundle.py
python -m http.server -d web 8000
```

Then open http://localhost:8000. To test against a local copy of the Pyodide distribution instead of the CDN, add `?pyodide=/path/to/pyodide/` to the URL.

Settings are kept in the URL hash, so a link reproduces them.

## Numbers

Pyodide 314.0.7 ships numpy 2.4.6 and scipy 1.18.0 rather than the pinned 2.4.1 and 1.17.0. `tests/test_web.py` checks `runner.py` against the model API.

## Publishing

`.github/workflows/pages.yml` bundles the model and deploys this folder to GitHub Pages on every push to `main`. Enable it once under Settings > Pages > Source: GitHub Actions. GitHub Pages is free only for public repositories.
