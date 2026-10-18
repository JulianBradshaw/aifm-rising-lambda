from aifm_sites import *
import numpy as np
from progress_model.progress_rate import compute_research_effort
import csv
rows = []
for mode in ['uplift-solved','time-horizon','revenue']:
    p = dict(preset('daniel-08-16-26'), parallel_penalty=0.5, ac_anchor_mode=mode)
    a = model_run(p, {}, detail=True); b = model_run(p, {'dynamics': 0.65}, detail=True)
    m = a['model']; R = m.results; t = np.asarray(R['times']); PD = p['present_day']; ac = a['ac']
    f = lambda k, tt: float(np.interp(tt, t, np.asarray(R[k], float)))
    L0, L1 = f('coding_labors', PD), f('coding_labors', ac)
    S0, S1 = f('serial_coding_labors', PD), f('serial_coding_labors', ac)
    G = L1/L0
    k = G**0.15
    P = m.params
    E1 = f('discounted_exp_compute', ac) if 'discounted_exp_compute' in R else None
    # static CES dilution at AC: research effort with serial labor x k
    import progress_model.progress_rate as pr
    ec = np.exp(np.interp(ac, m.data.time, np.log(m.data.experiment_H100e)))
    re0 = compute_research_effort(ec, S1, P.alpha_experiment_capacity, P.rho_experiment_capacity, P.experiment_compute_exponent, 1.0)
    re1 = compute_research_effort(ec, S1*k, P.alpha_experiment_capacity, P.rho_experiment_capacity, P.experiment_compute_exponent, 1.0)
    # elasticity
    re2 = compute_research_effort(ec, S1*1.01, P.alpha_experiment_capacity, P.rho_experiment_capacity, P.experiment_compute_exponent, 1.0)
    el = np.log(re2/re0)/np.log(1.01)
    sw_share = f('software_progress_rates', ac)/f('progress_rates', ac)
    sw_share0 = f('software_progress_rates', PD)/f('progress_rates', PD)
    # realized progress-rate ratio between runs (from integrated progress)
    tb = np.asarray(b['model'].results['times']); pb = np.asarray(b['model'].results['progress'])
    grid = np.linspace(PD, ac, 200)
    pa_g = np.interp(grid, t, R['progress']); pb_g = np.interp(grid, tb, pb)
    ra = np.gradient(pa_g, grid); rb = np.gradient(pb_g, grid)
    ratio = rb/ra
    avg_speed = (pb_g[-1]-pa_g[0])/(pa_g[-1]-pa_g[0]) - 1   # extra progress by AC date
    T = (ac-PD)*12
    print(f"\n{mode}: T={T:.1f} mo; L_opt today/at AC (x human-today) {L0/f('coding_labors',PD)*0+L0:.0f}->{L1:.0f}, growth G={G:.2f}; serial S growth {S1/S0:.2f}")
    print(f"  serial gain at AC G^0.15={k:.3f}; CES labor elasticity at AC {el:.3f}; research effort gain at AC {re1/re0:.3f}; infinite-labor headroom at AC {f('exp_cap_mult_with_infinite_labor', ac):.2f} (today {f('exp_cap_mult_with_infinite_labor', PD):.2f})")
    print(f"  software share of progress rate today {sw_share0:.2f}, at AC {sw_share:.2f}")
    print(f"  realized progress-rate ratio: at 25/50/75/100% of path {ratio[50]:.3f} {ratio[100]:.3f} {ratio[150]:.3f} {ratio[-2]:.3f}; extra progress by old AC date {100*avg_speed:.1f}% ; AC shift {12*(b['ac']-ac):+.2f} mo; T*s/(1+s)={T*avg_speed/(1+avg_speed):.2f}")
    rows.append(dict(anchor_mode=mode, months_today_to_ac=round(T,2), labor_growth_to_ac=round(G,1),
        serial_labor_gain_at_ac=round(k,4), throughput_gain_at_ac=round(float(re1/re0),4), progress_rate_gain_at_ac=round(float(ratio[-2]),4),
        avg_extra_progress=round(float(avg_speed),4), ac_shift_months=round(12*(b['ac']-ac),3)))
w = csv.DictWriter(open('benefit_dilution.csv','w',newline=''), fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
