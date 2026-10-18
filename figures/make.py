"""Regenerate the λ figures.

    python figures/make.py                 # redraw every figure from the committed data (seconds)
    python figures/make.py --rerun         # rerun the model sweeps first (an hour or more)
    python figures/make.py lambda_takeoff  # one group only

Each step runs with its group's folder as the working directory, so the data files and
figures land next to the scripts. Groups that run the model with each use of λ switched
separately (lambda_uses, lambda_takeoff) build a patched copy of upstream in
figures/.cache/ on first use; upstream/ itself is not modified.
"""
import os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))

# group: (model runs, writing data files; drawing steps, run in order)
GROUPS = {
    'lambda_sweep': (
        ['sweep.py', 'sweep_presets.py', 'sweep_anchors.py', 'sweep_lowlam.py'],
        ['plot.py', 'plot_presets.py', 'plot_anchors.py', 'plot_lowlam.py', 'plot_eta_asi.py', 'plot_eta_forms.py']),
    'coding_uplift': (['data.py'], ['plot.py']),
    'lambda_uses': (
        ['attrib2.py', 'benefit.py', 'benefit_avg.py', 'ces_split.py'],
        ['tables.py', 'plot.py 0.65', 'plot.py 1', 'plot_dilution.py', 'plot_drag.py']),
    'lambda_takeoff': (
        ['attrib.py', 'attrib_eta_net.py', 'attrib_eta_split.py', 'asym_benefit.py', 'asym_full.py', 'eta_sweep.py'],
        ['tables.py', 'tables_eta_net.py', 'tables_eta_split.py',
         'plot.py takeoff 0.65', 'plot.py takeoff 1', 'plot.py asi 0.65', 'plot.py asi 1',
         'plot_eta_net.py takeoff 0.65', 'plot_eta_net.py takeoff 1',
         'plot_eta_split.py takeoff 0.65', 'plot_eta_split.py takeoff 1',
         'plot_asymptote.py', 'plot_asym_benefit.py', 'plot_asym_pct.py', 'plot_asym_bars.py',
         'plot_eta.py', 'plot_r.py', 'plot_beta.py']),
    'eta_issue': ([], ['plot.py']),
    # Uses this repository's two-λ variant; draws the original model's lines from lambda_sweep's data.
    'two_lambda_anchors': (['sweep_anchors_two_lambda.py'], ['plot_anchors_two_lambda.py']),
}


def step(group, cmd):
    args = cmd.split()
    env = dict(os.environ, PYTHONPATH=os.pathsep.join([HERE, os.environ.get('PYTHONPATH', '')]), MPLBACKEND='Agg')
    t = time.time()
    print(f'{group}/{cmd}', end=' ', flush=True)
    subprocess.run([sys.executable, args[0], *args[1:]], cwd=os.path.join(HERE, group), env=env, check=True,
                   stdout=subprocess.DEVNULL)
    print(f'({time.time() - t:.0f} s)')


def main(argv):
    rerun = '--rerun' in argv
    groups = [a for a in argv if not a.startswith('--')] or list(GROUPS)
    for g in groups:
        runs, draws = GROUPS[g]
        for cmd in (runs if rerun else []) + draws:
            step(g, cmd)


if __name__ == '__main__':
    main(sys.argv[1:])
