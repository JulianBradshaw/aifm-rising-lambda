"""Pack the model sources the browser page needs into web/model.zip.

The page unpacks this zip into Pyodide's in-memory filesystem, so the browser
runs the same two_lambda and pinned upstream code as the command line.
Run from the repository root: python web/bundle.py
"""
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    *sorted((ROOT / 'two_lambda').glob('*.py')),
    *sorted((ROOT / 'upstream/progress_model').glob('*.py')),
    ROOT / 'upstream/inputs/input_data.csv',
    ROOT / 'upstream/inputs/metr/benchmark_results_1_1.yaml',
    ROOT / 'upstream/constants/parameters.ts',
    ROOT / 'upstream/LICENSE',
    ROOT / 'LICENSE',
]


def main():
    missing = [f for f in FILES if not f.exists()]
    if missing:
        raise SystemExit(f'Missing {missing}; run git submodule update --init')
    out = ROOT / 'web/model.zip'
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        for f in FILES:
            z.write(f, f.relative_to(ROOT).as_posix())
    print(f'Wrote {out} ({out.stat().st_size // 1024} KB, {len(FILES)} files)')


if __name__ == '__main__':
    main()
