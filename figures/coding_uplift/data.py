# Automation-fraction trajectories under the coding-uplift anchor, Daniel 08/16/26 preset,
# varying only the Aug 2026 serial coding uplift. Writes coding_uplift_curves.csv.
import os, sys, io, csv, contextlib, logging
import numpy as np
import aifm as run
ROOT = run.ROOT
with contextlib.redirect_stdout(io.StringIO()):
    from progress_model import ProgressModel
    from progress_model.parameters import Parameters
    from progress_model.time_series import generate_time_series_from_dict
    from api.index import drop_unknown_params
TS = ['constant_training_system_performance_growth_rate','slowdown_year','post_slowdown_training_system_performance_growth_rate']

def trajectory(p):
    with contextlib.redirect_stdout(io.StringIO()):
        params = Parameters(**drop_unknown_params({k: v for k, v in p.items() if k not in TS}))
        ts = generate_time_series_from_dict({k: p[k] for k in TS}, os.path.join(ROOT, 'inputs/input_data.csv'))
        m = ProgressModel(params, ts); m.compute_progress_trajectory([2017, 2200], 0.0)
    R = m.results
    return np.asarray(R['times']), np.asarray(R['automation_fraction'], float), np.asarray(R['serial_coding_labor_multipliers'], float), R['milestones']['AC']['time']

p = run.preset('daniel-08-16-26'); PD = p['present_day']
print('preset: uplift', p['serial_uplift_at_reference_date'], 'doubling', p['excess_uplift_doubling_time'], 'lambda', p['parallel_penalty'], 'anchor', p.get('ac_anchor_mode'), 'pd', PD)
rows = []
for up in [1.5, 2.0, 3.0]:
    t, f, s, ac = trajectory(dict(p, serial_uplift_at_reference_date=up))
    print(f"uplift {up}: f_now {np.interp(PD,t,f):.3f} serial_now {np.interp(PD,t,s):.2f} AC {ac:.3f} ({(ac-PD)*12:.1f} mo)")
    for tt in np.arange(2024.0, 2030.001, 1/24):
        rows.append(dict(uplift=up, year=round(tt,4), automated_fraction=round(float(np.interp(tt,t,f)),5), ac_year=round(ac,4)))
w = csv.DictWriter(open('coding_uplift_curves.csv','w',newline=''), fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
